# 🚀 QuantumBoom

An intelligent daily digest that fetches the latest quantum computing research and news, uses GPT for smart summarization, and auto-deploys to Netlify as a live website.

## ✨ Features

- **📚 Research Papers**: Fetches from curated Google Sheets databases
- **📄 arXiv Integration**: Latest quantum computing papers from arXiv
- **📰 News Aggregation**: Google News quantum computing headlines
- **🤖 GPT Summarization**: Intelligent, context-aware summaries
- **🌐 Auto-Deploy**: Automatically deploys to Netlify as a live website
- **🔄 Daily Automation**: Set up with cron for daily updates
- **📊 Logging**: Comprehensive logging and error handling

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to the project
cd app/QuantumBoom

# Run setup script
python setup.py
```

### 2. Configuration

Edit the `.env` file with your credentials:

```env
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration (required)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
RECIPIENT_EMAIL=recipient@example.com

# SMTP Settings (optional - defaults to Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3. Test Run

```bash
python quantumboom.py
```

## 📋 Requirements

- **Python 3.8+**
- **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Netlify Account** - Free account at [Netlify](https://netlify.com)
- **Netlify Site** - Create a new site for deployment

## 🔧 Configuration Details

### OpenAI API Key
1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Create an API key
3. Add to `.env` file

### Netlify Setup
1. Sign up at [Netlify](https://netlify.com)
2. Create a new site (can be empty initially)
3. Get your Site ID from Site settings → General → Site details
4. Generate Personal Access Token: User settings → Applications → Personal access tokens
5. Add both to `.env` file

### Data Sources
- **Research Papers**: Google Sheets CSV exports
- **arXiv**: Official arXiv API
- **News**: Google News RSS feed

## 🤖 GPT Integration

The script uses GPT-4 for intelligent summarization with context-specific prompts:

### Research Papers
- Identifies key findings and methodology
- Highlights novelty and practical implications
- Formats with proper HTML structure
- Avoids boilerplate language

### News Items
- Focuses on breakthroughs and market impacts
- Groups related stories
- Emphasizes actionable insights
- Includes source attribution

## 📅 Daily Automation

### Option 1: GitHub Actions (Recommended - Free)
```bash
# See GITHUB_ACTIONS_SETUP.md for detailed instructions
# Automatically runs daily at 8:00 AM UTC
# No server maintenance required
```

### Option 2: Linux/macOS (cron)
```bash
# Edit crontab
crontab -e

# Add daily run at 8:00 AM
0 8 * * * cd /path/to/app/QuantumBoom && python3 quantumboom.py >> logs/cron.log 2>&1
```

### Option 3: Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 8:00 AM
4. Action: Start program `python.exe`
5. Arguments: `quantumboom.py`
6. Start in: `C:\path\to\app\QuantumBoom`

## 📁 Project Structure

```
app/QuantumBoom/
├── quantumboom.py        # Main script
├── requirements.txt      # Python dependencies
├── setup.py             # Setup and installation
├── .env.template        # Environment configuration template
├── .env                 # Your actual configuration (created by setup)
├── .gitignore           # Git ignore file
├── README.md            # This file
├── GITHUB_ACTIONS_SETUP.md # GitHub Actions setup guide
├── cron_example.txt     # Cron job examples
├── .github/             # GitHub Actions workflows
│   └── workflows/
│       └── quantum-boom.yml # Daily deployment workflow
├── output/              # Output directory
│   ├── deploy/          # Netlify deployment files
│   │   ├── index.html   # Generated website
│   │   ├── _redirects   # Netlify redirects
│   │   └── robots.txt   # SEO robots file
│   └── digest_backup_*.html # Daily digest backups
└── logs/                # Log files directory
```

## 🔍 Troubleshooting

### Common Issues

**OpenAI API Errors**
- Check API key validity
- Verify account has credits
- Check rate limits

**Email Sending Fails**
- Use App Password for Gmail
- Check SMTP settings
- Verify firewall/antivirus settings

**No Content Fetched**
- Check internet connection
- Verify data source URLs
- Review logs for specific errors

### Logs
Check `quantumboom.log` for detailed execution information.

## 🎨 Customization

### Modify Data Sources
Edit the `sources` dictionary in `QuantumDigest.__init__()`:

```python
self.sources = {
    'research_list': 'your_custom_csv_url',
    'arxiv_api': 'modified_arxiv_query',
    # ... other sources
}
```

### Customize GPT Prompts
Modify `_create_summarization_prompt()` method for different summarization styles.

### HTML Styling
Edit `build_html_digest()` method to customize email appearance.

## 📊 Sample Output

The digest includes:
- **Research Paper Highlights**: Key findings from curated papers
- **Latest arXiv Papers**: Recent submissions with intelligent summaries
- **Recent News & Developments**: Market updates and breakthroughs

Each section is beautifully formatted with:
- Clean HTML styling
- Responsive design
- Professional typography
- Color-coded sections

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the digest!

## 📄 License

MIT License - feel free to use and modify for your needs.

---

**Happy quantum computing! 🚀**
