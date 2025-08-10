# 🚀 QuantumBoom Netlify Setup Guide

This guide will help you set up QuantumBoom to automatically deploy to Netlify.

## 📋 Prerequisites

- Netlify account (free)
- OpenAI API key
- Python 3.8+

## 🔧 Step-by-Step Setup

### 1. Create Netlify Site

1. Go to [Netlify](https://netlify.com) and sign up/log in
2. Click "Add new site" → "Deploy manually"
3. Create a simple `index.html` file with:
   ```html
   <!DOCTYPE html>
   <html>
   <head><title>QuantumBoom</title></head>
   <body><h1>QuantumBoom Coming Soon...</h1></body>
   </html>
   ```
4. Drag and drop this file to deploy
5. Note your site URL (e.g., `amazing-site-123.netlify.app`)

### 2. Get Site ID

1. Go to Site settings → General → Site details
2. Copy the **Site ID** (looks like: `12345678-1234-1234-1234-123456789abc`)

### 3. Generate Access Token

1. Go to User settings (click your avatar) → Applications
2. Click "Personal access tokens" → "New access token"
3. Give it a name like "QuantumBoom"
4. Set expiration (recommend 1 year)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

### 4. Configure Environment Variables

Edit your `.env` file:

```env
# QuantumBoom Environment Configuration

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Netlify Configuration
NETLIFY_ACCESS_TOKEN=your_netlify_access_token_here
NETLIFY_SITE_ID=your_netlify_site_id_here
```

### 5. Test Deployment

Run QuantumBoom:

```bash
cd app/QuantumBoom
python quantumboom.py
```

You should see:
- ✅ Data fetching from sources
- ✅ HTML generation
- ✅ Deployment to Netlify
- 🌐 Your live site URL

### 6. Set Up Daily Automation

#### Linux/macOS (cron):
```bash
# Edit crontab
crontab -e

# Add daily run at 8:00 AM
0 8 * * * cd /path/to/app/QuantumBoom && python3 quantumboom.py >> logs/cron.log 2>&1
```

#### Windows (Task Scheduler):
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 8:00 AM
4. Action: Start program `python.exe`
5. Arguments: `quantumboom.py`
6. Start in: `C:\path\to\app\QuantumBoom`

## 🎯 What Happens

1. **Data Collection**: Fetches latest quantum research and news
2. **AI Summarization**: Uses GPT to create intelligent summaries
3. **HTML Generation**: Creates beautiful, responsive website
4. **Auto-Deploy**: Pushes to Netlify via API
5. **Live Site**: Your site updates automatically!

## 🌐 Your Live Site

After setup, your quantum computing digest will be live at:
`https://your-site-id.netlify.app`

The site updates automatically every time you run the script!

## 🔍 Troubleshooting

### Common Issues:

**"Missing environment variables"**
- Check your `.env` file has all required variables
- Ensure no extra spaces around the `=` sign

**"Deployment failed: 401"**
- Your Netlify access token is invalid or expired
- Generate a new token and update `.env`

**"Deployment failed: 404"**
- Your site ID is incorrect
- Check Site settings → General → Site details

**"OpenAI quota exceeded"**
- Add credits to your OpenAI account
- Or use the `preview_no_gpt.py` script for testing

### Check Logs:
```bash
tail -f quantumboom.log
```

## 🎉 Success!

Once set up, you'll have:
- 🌐 **Live website** updating daily
- 📊 **Latest quantum research** automatically summarized
- 🚀 **Zero maintenance** - runs automatically
- 📱 **Mobile responsive** - works on all devices

Your quantum computing digest is now live and updating automatically! 🎊
