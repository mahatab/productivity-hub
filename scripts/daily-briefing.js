#!/usr/bin/env node

/**
 * Daily Morning Briefing Generator
 * Combines browser news extraction with web search fallback
 * Outputs clean text for email delivery
 */

const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

async function getNewsFromBrowser() {
  console.log('📰 Fetching news via browser...');
  
  // Use Clawdbot browser tool to visit news sites
  // This would be called by Rudro via browser tool
  // Returns structured text headlines
  
  return {
    bangladesh: [],
    usa: [],
    international: [],
    sports: []
  };
}

async function getNewsFromSearch() {
  console.log('🔍 Fetching news via web search...');
  
  // Fallback to web_search API
  // Called by Rudro when browser method fails
  
  return {
    bangladesh: [],
    usa: [],
    international: [],
    sports: []
  };
}

async function generateBriefing() {
  const today = new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
  
  console.log(`📋 Generating briefing for ${today}...`);
  
  // Try browser first, fallback to search
  let news;
  try {
    news = await getNewsFromBrowser();
    if (!news.international.length) {
      console.log('⚠️ Browser returned no results, trying search...');
      news = await getNewsFromSearch();
    }
  } catch (error) {
    console.log('❌ Browser failed, using search:', error.message);
    news = await getNewsFromSearch();
  }
  
  // Format the briefing
  const briefing = formatBriefing(today, news);
  
  return briefing;
}

function formatBriefing(date, news) {
  let text = `Good morning Big Giant Head! ☀️\n\n`;
  text += `Here's your daily briefing for ${date}:\n\n`;
  
  // Breaking news if any
  if (news.breaking && news.breaking.length > 0) {
    text += `⚡ BREAKING NEWS\n`;
    news.breaking.forEach(item => {
      text += `• ${item.headline} (${item.source}, ${item.time})\n`;
    });
    text += `\n`;
  }
  
  // Bangladesh
  text += `📰 TOP NEWS\n\n`;
  text += `**BANGLADESH**\n`;
  news.bangladesh.forEach(item => {
    text += `• ${item.headline} (${item.source}, ${item.date})\n`;
  });
  text += `\n`;
  
  // USA
  text += `**USA**\n`;
  news.usa.forEach(item => {
    text += `• ${item.headline} (${item.source}, ${item.date})\n`;
  });
  text += `\n`;
  
  // International
  text += `**INTERNATIONAL**\n`;
  news.international.forEach(item => {
    text += `• ${item.headline} (${item.source}, ${item.date})\n`;
  });
  text += `\n`;
  
  // Sports
  text += `🏅 GAMES ON TV TODAY\n\n`;
  news.sports.forEach(item => {
    text += `• ${item.match}\n  Time: ${item.time}\n  Channel: ${item.channel}\n`;
  });
  text += `\n`;
  
  // Ideas and quote
  text += `💡 NEW IDEAS (m2labs)\n\n`;
  if (news.idea) {
    text += `**${news.idea.title}**\n`;
    text += `${news.idea.description}\n\n`;
    text += `✨ Built a prototype for you!\n`;
    text += `Location: ${news.idea.path}\n`;
    text += `Screenshot: ${news.idea.screenshot}\n\n`;
  } else {
    text += `[No new idea generated today]\n\n`;
  }
  
  text += `✨ INSPIRATIONAL QUOTE\n\n`;
  text += `${news.quote || '[Daily quote]'}\n\n`;
  
  return text;
}

// Export for use in other scripts
module.exports = { generateBriefing, getNewsFromBrowser, getNewsFromSearch };

// Run if called directly
if (require.main === module) {
  generateBriefing()
    .then(briefing => {
      console.log('\n✅ Briefing generated:\n');
      console.log(briefing);
    })
    .catch(err => {
      console.error('❌ Failed to generate briefing:', err);
      process.exit(1);
    });
}
