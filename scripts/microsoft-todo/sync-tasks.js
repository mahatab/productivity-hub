#!/usr/bin/env node

/**
 * Microsoft To Do Sync via Graph API
 * Syncs tasks from Microsoft To Do to HEARTBEAT.md
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const CONFIG_PATH = path.join(__dirname, 'config.json');
const TOKEN_PATH = path.join(__dirname, 'token.json');
const HEARTBEAT_PATH = '/Users/mahatabrashid/clawd/HEARTBEAT.md';

// Microsoft Graph API endpoints
const GRAPH_API = 'https://graph.microsoft.com/v1.0';
const AUTH_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0';

/**
 * Make an HTTPS request
 */
function httpsRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ statusCode: res.statusCode, data: JSON.parse(data) });
        } catch (e) {
          resolve({ statusCode: res.statusCode, data });
        }
      });
    });
    req.on('error', reject);
    if (options.body) req.write(options.body);
    req.end();
  });
}

/**
 * Get access token (refresh if needed)
 */
async function getAccessToken() {
  if (!fs.existsSync(CONFIG_PATH)) {
    throw new Error('Config file not found. Run setup first.');
  }
  
  const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  let token = fs.existsSync(TOKEN_PATH) ? JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf8')) : null;
  
  // Check if token is expired
  if (token && token.expires_at > Date.now()) {
    return token.access_token;
  }
  
  // Refresh token
  if (token && token.refresh_token) {
    const params = new URLSearchParams({
      client_id: config.client_id,
      client_secret: config.client_secret,
      refresh_token: token.refresh_token,
      grant_type: 'refresh_token'
    });
    
    const result = await httpsRequest(`${AUTH_URL}/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params.toString()
    });
    
    if (result.data.access_token) {
      token = {
        access_token: result.data.access_token,
        refresh_token: result.data.refresh_token || token.refresh_token,
        expires_at: Date.now() + (result.data.expires_in * 1000)
      };
      fs.writeFileSync(TOKEN_PATH, JSON.stringify(token, null, 2));
      return token.access_token;
    }
  }
  
  throw new Error('No valid token. Please run authentication flow.');
}

/**
 * Fetch tasks from Microsoft To Do
 */
async function fetchTasks() {
  const token = await getAccessToken();
  const url = new URL(`${GRAPH_API}/me/todo/lists`);
  
  const listsResponse = await httpsRequest(url.toString(), {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (listsResponse.statusCode !== 200) {
    throw new Error(`Failed to fetch lists: ${JSON.stringify(listsResponse.data)}`);
  }
  
  const lists = listsResponse.data.value;
  const allTasks = [];
  
  for (const list of lists) {
    const tasksUrl = `${GRAPH_API}/me/todo/lists/${list.id}/tasks`;
    const tasksResponse = await httpsRequest(tasksUrl, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (tasksResponse.statusCode === 200) {
      const tasks = tasksResponse.data.value
        .filter(t => t.status !== 'completed')
        .map(t => ({
          title: t.title,
          list: list.displayName,
          importance: t.importance,
          dueDate: t.dueDateTime?.dateTime,
          createdDate: t.createdDateTime
        }));
      allTasks.push(...tasks);
    }
  }
  
  return allTasks;
}

/**
 * Update HEARTBEAT.md with synced tasks
 */
function updateHeartbeat(tasks) {
  if (!fs.existsSync(HEARTBEAT_PATH)) {
    console.error('HEARTBEAT.md not found');
    return;
  }
  
  const heartbeat = fs.readFileSync(HEARTBEAT_PATH, 'utf8');
  const now = new Date().toISOString().split('T')[0];
  
  // Group tasks by importance/category
  const urgent = tasks.filter(t => t.importance === 'high');
  const normal = tasks.filter(t => t.importance === 'normal' || t.importance === 'low');
  
  // Build new Microsoft To Do section
  let todoSection = '\n## 📋 MICROSOFT TO DO (Synced)\n';
  todoSection += `*Last sync: ${now}*\n\n`;
  
  if (urgent.length > 0) {
    todoSection += '**HIGH PRIORITY:**\n';
    urgent.forEach(t => {
      const due = t.dueDate ? ` (due: ${t.dueDate.split('T')[0]})` : '';
      todoSection += `- [ ] ${t.title}${due} [${t.list}]\n`;
    });
    todoSection += '\n';
  }
  
  if (normal.length > 0) {
    todoSection += '**NORMAL:**\n';
    normal.forEach(t => {
      const due = t.dueDate ? ` (due: ${t.dueDate.split('T')[0]})` : '';
      todoSection += `- [ ] ${t.title}${due} [${t.list}]\n`;
    });
  }
  
  // Replace existing Microsoft To Do section or append
  const msToDoRegex = /\n## 📋 MICROSOFT TO DO.*?(?=\n## |$)/s;
  let updatedHeartbeat;
  
  if (msToDoRegex.test(heartbeat)) {
    updatedHeartbeat = heartbeat.replace(msToDoRegex, todoSection);
  } else {
    // Insert before Daily Email Format section
    const emailFormatIndex = heartbeat.indexOf('## Daily Email Format');
    if (emailFormatIndex > -1) {
      updatedHeartbeat = heartbeat.slice(0, emailFormatIndex) + todoSection + '\n' + heartbeat.slice(emailFormatIndex);
    } else {
      updatedHeartbeat = heartbeat + '\n' + todoSection;
    }
  }
  
  fs.writeFileSync(HEARTBEAT_PATH, updatedHeartbeat);
  console.log(`✅ Synced ${tasks.length} tasks to HEARTBEAT.md`);
}

/**
 * Main sync function
 */
async function sync() {
  try {
    console.log('🔄 Syncing Microsoft To Do tasks...');
    const tasks = await fetchTasks();
    updateHeartbeat(tasks);
    console.log(`✅ Sync complete! Found ${tasks.length} incomplete tasks.`);
  } catch (error) {
    console.error('❌ Sync failed:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  sync();
}

module.exports = { sync, fetchTasks };
