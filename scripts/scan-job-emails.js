#!/usr/bin/env node
/**
 * Job Email Scanner - AI-powered job email detection
 * Scans inbox for job-related emails and outputs structured data
 * for the job dashboard
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const WORKSPACE_DIR = path.join(__dirname, '..');
const JOBS_DIR = path.join(WORKSPACE_DIR, 'jobs');
const TEMP_FILE = '/tmp/job-emails.txt';

console.log('📧 Scanning inbox for job-related emails...\n');

try {
    // Fetch recent emails using himalaya
    const emailList = execSync('himalaya envelope list --account rudro --page-size 100', {
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'ignore']
    });

    // Parse email list and filter for job-related keywords
    const lines = emailList.split('\n').filter(line => line.trim());
    const jobKeywords = /(application|interview|offer|position|job|career|hiring|recruiter|opportunity|applied|thanks for applying|application received|next steps)/i;
    
    const potentialJobEmails = lines.filter(line => jobKeywords.test(line));
    
    console.log(`✅ Found ${lines.length} total emails`);
    console.log(`🔍 Found ${potentialJobEmails.length} potentially job-related emails\n`);

    if (potentialJobEmails.length === 0) {
        console.log('✅ No new job emails found');
        process.exit(0);
    }

    // Extract email IDs from table format (| ID | ...)
    const emailIds = potentialJobEmails
        .slice(0, 20) // Process max 20 emails
        .map(line => {
            // Parse table format: | 11 |  *    | Subject ...
            const match = line.match(/\|\s*(\d+)\s*\|/);
            return match ? match[1] : null;
        })
        .filter(id => id && !isNaN(id));

    console.log(`📥 Fetching ${emailIds.length} emails for AI analysis...\n`);

    // Fetch full email content
    let emailsContent = [];
    
    for (const id of emailIds) {
        try {
            const content = execSync(`himalaya message read --account rudro ${id}`, {
                encoding: 'utf8',
                stdio: ['pipe', 'pipe', 'ignore']
            });
            
            emailsContent.push({
                id: id,
                content: content.substring(0, 2000) // Limit content size
            });
            
            process.stdout.write('.');
        } catch (err) {
            // Skip failed emails
        }
    }
    
    console.log(`\n\n✅ Fetched ${emailsContent.length} emails successfully\n`);

    // Save to temp file for AI processing
    const output = emailsContent.map((email, index) => {
        return `\n========== EMAIL ${index + 1} (ID: ${email.id}) ==========\n${email.content}\n`;
    }).join('\n');

    fs.writeFileSync(TEMP_FILE, output);
    
    console.log(`📄 Email content saved to: ${TEMP_FILE}`);
    console.log(`\n🤖 Ready for AI analysis!`);
    console.log(`\nNext: Clawdbot will analyze these emails and extract job information.\n`);

    // Output JSON structure for easy parsing
    const summary = {
        total_emails: emailsContent.length,
        temp_file: TEMP_FILE,
        timestamp: new Date().toISOString(),
        email_ids: emailsContent.map(e => e.id)
    };

    console.log('Summary:', JSON.stringify(summary, null, 2));

} catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
}
