#!/usr/bin/env node

/**
 * Microsoft To Do Setup - OAuth Authentication Flow
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { exec } = require('child_process');

const CONFIG_PATH = path.join(__dirname, 'config.json');
const TOKEN_PATH = path.join(__dirname, 'token.json');

console.log('🔐 Microsoft To Do - OAuth Setup\n');

// Step 1: Check for existing config
if (fs.existsSync(CONFIG_PATH) && fs.existsSync(TOKEN_PATH)) {
  console.log('✅ Authentication already configured!');
  console.log('Run: node sync-tasks.js to test the sync\n');
  process.exit(0);
}

console.log('📋 SETUP INSTRUCTIONS:\n');
console.log('You need to register an Azure AD application to get credentials.\n');
console.log('🔗 Go to: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade\n');
console.log('Steps:');
console.log('1. Click "New registration"');
console.log('2. Name: "Rudro Microsoft To Do Sync"');
console.log('3. Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"');
console.log('4. Redirect URI: Select "Public client/native (mobile & desktop)" → http://localhost:8080/callback');
console.log('5. Click "Register"\n');
console.log('6. In the app overview, copy the "Application (client) ID"');
console.log('7. Go to "Certificates & secrets" → "New client secret" → Copy the secret VALUE\n');
console.log('8. Go to "API permissions" → "Add a permission"');
console.log('   → "Microsoft Graph" → "Delegated permissions"');
console.log('   → Add: Tasks.ReadWrite, User.Read');
console.log('   → Click "Grant admin consent" (optional but recommended)\n');

const readline = require('readline').createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(query) {
  return new Promise(resolve => readline.question(query, resolve));
}

async function setup() {
  const clientId = await question('Enter your Application (client) ID: ');
  const clientSecret = await question('Enter your Client Secret: ');
  
  if (!clientId || !clientSecret) {
    console.error('❌ Both Client ID and Client Secret are required!');
    process.exit(1);
  }
  
  // Save config
  const config = {
    client_id: clientId.trim(),
    client_secret: clientSecret.trim(),
    redirect_uri: 'http://localhost:8080/callback',
    scopes: 'Tasks.ReadWrite User.Read offline_access'
  };
  
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  console.log('\n✅ Config saved!\n');
  
  // Generate authorization URL
  const authUrl = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?` +
    `client_id=${config.client_id}&` +
    `response_type=code&` +
    `redirect_uri=${encodeURIComponent(config.redirect_uri)}&` +
    `scope=${encodeURIComponent(config.scopes)}`;
  
  console.log('🔗 NEXT STEP: Authenticate with Microsoft\n');
  console.log('Opening browser to sign in...\n');
  console.log('Authorization URL:');
  console.log(authUrl);
  console.log('\n');
  
  // Open browser
  const openCmd = process.platform === 'darwin' ? 'open' : 
                   process.platform === 'win32' ? 'start' : 'xdg-open';
  exec(`${openCmd} "${authUrl}"`);
  
  console.log('After you authorize, you\'ll be redirected to localhost:8080/callback');
  console.log('Copy the FULL redirect URL (including ?code=...) and paste it here:\n');
  
  const redirectUrl = await question('Paste the redirect URL: ');
  const codeMatch = redirectUrl.match(/code=([^&]+)/);
  
  if (!codeMatch) {
    console.error('❌ Could not find authorization code in URL!');
    process.exit(1);
  }
  
  const code = codeMatch[1];
  console.log('\n🔄 Exchanging code for access token...\n');
  
  // Exchange code for token
  const params = new URLSearchParams({
    client_id: config.client_id,
    client_secret: config.client_secret,
    code: code,
    redirect_uri: config.redirect_uri,
    grant_type: 'authorization_code'
  });
  
  const tokenUrl = 'https://login.microsoftonline.com/common/oauth2/v2.0/token';
  
  return new Promise((resolve, reject) => {
    const req = https.request(tokenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.access_token) {
            const token = {
              access_token: result.access_token,
              refresh_token: result.refresh_token,
              expires_at: Date.now() + (result.expires_in * 1000)
            };
            fs.writeFileSync(TOKEN_PATH, JSON.stringify(token, null, 2));
            console.log('✅ Authentication successful!');
            console.log('✅ Token saved!\n');
            console.log('🎉 Setup complete! You can now run: node sync-tasks.js\n');
            resolve();
          } else {
            console.error('❌ Token exchange failed:', result);
            reject(new Error('Token exchange failed'));
          }
        } catch (e) {
          console.error('❌ Parse error:', e);
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.write(params.toString());
    req.end();
  });
}

setup()
  .then(() => {
    readline.close();
    process.exit(0);
  })
  .catch(err => {
    console.error('Setup failed:', err);
    readline.close();
    process.exit(1);
  });
