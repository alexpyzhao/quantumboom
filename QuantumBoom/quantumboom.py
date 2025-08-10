#!/usr/bin/env python3
"""
QuantumBoom - Daily quantum computing research & news summarizer
Fetches latest quantum research and news, uses GPT for intelligent summarization,
and auto-deploys to Netlify as a live website.
"""

import os
import sys
import logging
import pandas as pd
import feedparser
import requests
from datetime import datetime, timedelta
# from openai import OpenAI  # Removed for no-GPT version
from typing import List, Dict, Tuple
import time
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantumboom.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class QuantumBoom:
    def __init__(self):
        """Initialize QuantumBoom with configuration."""
        # self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Removed for no-GPT version
        self.netlify_config = {
            'access_token': os.getenv('NETLIFY_ACCESS_TOKEN'),
            'site_id': os.getenv('NETLIFY_SITE_ID'),
            'api_base': 'https://api.netlify.com/api/v1'
        }
        
        # Data source URLs
        self.sources = {
            'research_list': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTjka1LpVvM74sNMqcZCxh0WsQXi8IUbIknLEojpmSysEeQUG2BStQNGwdgKD9Q9jkzAAtDmcMrLYG5/pub?output=csv',
            'research_brief': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQQGTFKG6AKhJVLBujShiHC6vtQ9gbN5TSnrcEqzElOsCJTkRdPYXNThJJQNhHSY68Z0-zfiJffhz64/pub?output=csv',
            'arxiv_api': 'https://export.arxiv.org/api/query?search_query=ti:%22quantum%20computing%22&sortBy=lastUpdatedDate&sortOrder=descending&max_results=10',
            'arxiv_players_api': 'https://export.arxiv.org/api/query?search_query=all%3A%22Xanadu%22+OR+all%3A%22IBM%22+OR+all%3A%22Google%22+OR+all%3A%22Rigetti%22+OR+all%3A%22Fujitsu%22+OR+all%3A%22Alice+%26+Bob%22+OR+all%3A%22Intel%22+OR+all%3A%22QuEra%22+OR+all%3A%22Pasqal%22+OR+all%3A%22Atom+Computing%22+OR+all%3A%22Infleqtion%22+OR+all%3A%22IonQ%22+OR+all%3A%22Quantinuum%22+OR+all%3A%22Alpine+Quantum+Technologies%22+OR+all%3A%22photonic+networks%22+OR+all%3A%22superconducting+qubits%22+OR+all%3A%22spin+qubits%22+OR+all%3A%22neutral+atoms%22+OR+all%3A%22trapped+ions%22&sortBy=lastUpdatedDate&sortOrder=descending&max_results=8',
            'google_news': 'https://news.google.com/rss/search?q=quantum+computing'
        }
        
        self.validate_config()

    def validate_config(self):
        """Validate required environment variables."""
        required_vars = ['NETLIFY_ACCESS_TOKEN', 'NETLIFY_SITE_ID']  # Removed OPENAI_API_KEY
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            sys.exit(1)

        logger.info("Configuration validated successfully")

    def fetch_csv(self, url: str, source_name: str) -> pd.DataFrame:
        """Fetch and parse CSV data from Google Sheets."""
        try:
            logger.info(f"Fetching {source_name} from {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV content
            df = pd.read_csv(pd.io.common.StringIO(response.text))
            logger.info(f"Successfully fetched {len(df)} rows from {source_name}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {source_name}: {str(e)}")
            return pd.DataFrame()

    def fetch_arxiv(self) -> List[Dict]:
        """Fetch latest quantum computing papers from arXiv."""
        try:
            logger.info("Fetching arXiv papers")
            feed = feedparser.parse(self.sources['arxiv_api'])
            
            papers = []
            for entry in feed.entries[:10]:  # Limit to 10 most recent
                paper = {
                    'title': entry.title,
                    'authors': ', '.join([author.name for author in entry.authors]),
                    'abstract': entry.summary,
                    'link': entry.link,
                    'published': entry.published,
                    'updated': entry.updated
                }
                papers.append(paper)
            
            logger.info(f"Successfully fetched {len(papers)} arXiv papers")
            return papers
            
        except Exception as e:
            logger.error(f"Error fetching arXiv papers: {str(e)}")
            return []

    def fetch_arxiv_players(self) -> List[Dict]:
        """Fetch latest quantum computing papers from major players and technologies."""
        try:
            logger.info("Fetching arXiv papers from quantum computing players")
            feed = feedparser.parse(self.sources['arxiv_players_api'])

            papers = []
            for entry in feed.entries[:8]:  # Limit to 8 for this section
                paper = {
                    'title': entry.title,
                    'authors': ', '.join([author.name for author in entry.authors]),
                    'abstract': entry.summary,
                    'link': entry.link,
                    'published': entry.published,
                    'updated': entry.updated
                }
                papers.append(paper)

            logger.info(f"Successfully fetched {len(papers)} arXiv papers from quantum players")
            return papers

        except Exception as e:
            logger.error(f"Error fetching arXiv players papers: {str(e)}")
            return []

    def fetch_news(self) -> List[Dict]:
        """Fetch latest quantum computing news from Google News."""
        try:
            logger.info("Fetching Google News")
            feed = feedparser.parse(self.sources['google_news'])
            
            news_items = []
            for entry in feed.entries[:15]:  # Limit to 15 most recent
                news_item = {
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'source': entry.source.title if hasattr(entry, 'source') else 'Unknown'
                }
                news_items.append(news_item)
            
            logger.info(f"Successfully fetched {len(news_items)} news items")
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []

    def format_research_papers(self, research_content: List[Dict]) -> str:
        """Format research papers without GPT."""
        if not research_content:
            return "<div class='article'><div class='content'>No research papers available today.</div></div>"

        html = ""
        for i, paper in enumerate(research_content[:4]):  # Limit to 4
            # Use the correct column names from the CSV
            title = paper.get('Title', 'Research Paper')
            authors = paper.get('Authors', 'Research Team')
            abstract = paper.get('Abstract', 'Abstract not available')

            # Clean up the data and handle NaN values
            title = str(title).strip() if title and str(title) != 'nan' else 'Research Paper'
            authors = str(authors).strip() if authors and str(authors) != 'nan' else 'Research Team'
            abstract = str(abstract).strip() if abstract and str(abstract) != 'nan' else 'Abstract not available'

            # Additional cleanup for empty strings
            if not title or title == '':
                title = 'Research Paper'
            if not authors or authors == '':
                authors = 'Research Team'
            if not abstract or abstract == '':
                abstract = 'Abstract not available'

            # Get additional fields
            pdf_link = paper.get('PDF Link', '')
            submission_date = paper.get('Submission Date', '')
            arxiv_id = paper.get('arXiv ID', '')

            # Truncate abstract
            if len(abstract) > 300:
                abstract = abstract[:300] + "..."

            # Build the HTML with links if available
            title_html = f'<a href="{pdf_link}" target="_blank">{title}</a>' if pdf_link and str(pdf_link) != 'nan' else title

            # Format submission date
            date_info = f" • <span class='date'>Submitted: {submission_date[:10]}</span>" if submission_date and str(submission_date) != 'nan' else ""
            arxiv_info = f" • <em>arXiv: {arxiv_id}</em>" if arxiv_id and str(arxiv_id) != 'nan' else ""

            html += f"""
            <article class="article">
                <h3>{title_html}</h3>
                <div class="meta">
                    <span class="author">{authors}</span>{date_info}{arxiv_info}
                </div>
                <div class="content">{abstract}</div>
            </article>
            """

        return html

    def format_arxiv_papers(self, arxiv_papers: List[Dict]) -> str:
        """Format arXiv papers without GPT."""
        if not arxiv_papers:
            return "<div class='article'><div class='content'>No arXiv papers available today.</div></div>"

        html = ""
        for i, paper in enumerate(arxiv_papers):
            title = paper['title']
            authors = paper['authors']
            abstract = paper['abstract']
            link = paper['link']
            published = paper.get('published', 'Unknown date')

            # Truncate abstract
            if len(abstract) > 400:
                abstract = abstract[:400] + "..."

            html += f"""
            <article class="article">
                <h3><a href="{link}" target="_blank">{title}</a></h3>
                <div class="meta">
                    <span class="author">{authors}</span> • <span class="date">Published: {published[:10]}</span>
                </div>
                <div class="content">{abstract}</div>
            </article>
            """

        return html

    def format_arxiv_players_papers(self, arxiv_players_papers: List[Dict]) -> str:
        """Format arXiv papers from quantum computing players without GPT."""
        if not arxiv_players_papers:
            return "<div class='article'><div class='content'>No papers from quantum computing players available today.</div></div>"

        html = ""
        for i, paper in enumerate(arxiv_players_papers):
            title = paper['title']
            authors = paper['authors']
            abstract = paper['abstract']
            link = paper['link']
            published = paper.get('published', 'Unknown date')

            # Truncate abstract
            if len(abstract) > 400:
                abstract = abstract[:400] + "..."

            html += f"""
            <article class="article">
                <h3><a href="{link}" target="_blank">{title}</a></h3>
                <div class="meta">
                    <span class="author">{authors}</span> • <span class="date">Published: {published[:10]}</span>
                </div>
                <div class="content">{abstract}</div>
            </article>
            """

        return html

    def format_news(self, news_items: List[Dict]) -> str:
        """Format news items without GPT."""
        if not news_items:
            return "<div class='article'><div class='content'>No news available today.</div></div>"

        html = ""
        for i, item in enumerate(news_items):
            title = item['title']
            link = item['link']
            source = item.get('source', 'Unknown Source')
            published = item.get('published', 'Unknown date')

            html += f"""
            <article class="article">
                <h3><a href="{link}" target="_blank">{title}</a></h3>
                <div class="meta">
                    <span class="author">{source}</span> • <span class="date">{published[:16] if published != 'Unknown date' else published}</span>
                </div>
            </article>
            """

        return html

# Removed GPT helper methods - using direct formatting instead

    def build_html_digest(self, formatted_content: Dict[str, str], stats: Dict[str, int]) -> str:
        """Build the complete HTML digest for the website."""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%H:%M")

        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>QuantumBoom - {current_date}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    line-height: 1.6;
                    color: #1a1a1a;
                    background-color: #ffffff;
                    font-size: 16px;
                }}

                .container {{
                    max-width: 680px;
                    margin: 0 auto;
                    padding: 0 20px;
                }}

                .header {{
                    background: #000;
                    color: white;
                    padding: 40px 0;
                    margin-bottom: 40px;
                }}

                .header h1 {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 8px;
                    letter-spacing: -0.02em;
                }}

                .header .subtitle {{
                    font-size: 1.1rem;
                    color: #999;
                    font-weight: 400;
                }}

                .stats {{
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 40px;
                }}

                .stats h3 {{
                    font-size: 1.1rem;
                    font-weight: 600;
                    margin-bottom: 12px;
                    color: #1a1a1a;
                }}

                .stats p {{
                    font-size: 0.95rem;
                    color: #666;
                    line-height: 1.5;
                }}

                .section {{
                    margin-bottom: 50px;
                }}

                .section-header {{
                    cursor: pointer;
                    user-select: none;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 16px 0;
                    border-bottom: 2px solid #00d084;
                    margin-bottom: 24px;
                    transition: all 0.3s ease;
                }}

                .section-header:hover {{
                    background-color: #f8f9fa;
                    margin: 0 -20px 24px -20px;
                    padding: 16px 20px;
                    border-radius: 8px;
                }}

                .section h2 {{
                    font-size: 1.8rem;
                    font-weight: 700;
                    color: #1a1a1a;
                    margin: 0;
                    letter-spacing: -0.01em;
                }}

                .toggle-icon {{
                    font-size: 1.5rem;
                    color: #00d084;
                    font-weight: bold;
                    transition: transform 0.3s ease;
                }}

                .section-content {{
                    transition: all 0.3s ease;
                    overflow: hidden;
                }}

                .section-content.collapsed {{
                    max-height: 0;
                    opacity: 0;
                    margin-bottom: 0;
                }}

                .section-content.expanded {{
                    max-height: none;
                    opacity: 1;
                }}

                .article {{
                    margin-bottom: 32px;
                    padding-bottom: 32px;
                    border-bottom: 1px solid #e9ecef;
                }}

                .article:last-child {{
                    border-bottom: none;
                    margin-bottom: 0;
                    padding-bottom: 0;
                }}

                .article h3 {{
                    font-size: 1.4rem;
                    font-weight: 600;
                    line-height: 1.3;
                    margin-bottom: 12px;
                    color: #1a1a1a;
                    letter-spacing: -0.01em;
                }}

                .article h3 a {{
                    color: #1a1a1a;
                    text-decoration: none;
                    transition: color 0.2s ease;
                }}

                .article h3 a:hover {{
                    color: #00d084;
                }}

                .article .meta {{
                    font-size: 0.9rem;
                    color: #666;
                    margin-bottom: 16px;
                    font-weight: 400;
                }}

                .article .meta .author {{
                    color: #00d084;
                    font-weight: 500;
                }}

                .article .meta .date {{
                    color: #999;
                }}

                .article .content {{
                    font-size: 1rem;
                    line-height: 1.7;
                    color: #333;
                }}

                .footer {{
                    border-top: 1px solid #e9ecef;
                    padding: 40px 0;
                    text-align: center;
                    color: #666;
                    font-size: 0.9rem;
                    margin-top: 60px;
                }}

                .footer p {{
                    margin-bottom: 8px;
                }}

                a {{
                    color: #00d084;
                    text-decoration: none;
                }}

                a:hover {{
                    text-decoration: underline;
                }}

                @media (max-width: 768px) {{
                    .container {{
                        padding: 0 16px;
                    }}

                    .header h1 {{
                        font-size: 2rem;
                    }}

                    .section h2 {{
                        font-size: 1.5rem;
                    }}

                    .article h3 {{
                        font-size: 1.2rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <header class="header">
                <div class="container">
                    <h1>🚀 QuantumBoom</h1>
                    <div class="subtitle">Daily Quantum Computing Research & News • {current_date} • {current_time}</div>
                </div>
            </header>

            <main class="container">
                <div class="stats">
                    <h3>📊 Today's Data Collection</h3>
                    <p>
                        <strong>News items:</strong> {stats.get('news_items', 0)} articles gathered<br>
                        <strong>Technology papers:</strong> {stats.get('arxiv_papers', 0)} papers fetched<br>
                        <strong>Company papers:</strong> {stats.get('arxiv_players_papers', 0)} papers from major players<br>
                        <strong>Highlighted papers:</strong> {stats.get('research_papers', 0)} papers collected<br>
                        <strong>Total sources:</strong> 5 data feeds processed
                    </p>
                </div>

                <section class="section">
                    <div class="section-header">
                        <h2>📰 News Items</h2>
                        <span class="toggle-icon">−</span>
                    </div>
                    <div class="section-content expanded">
                        {formatted_content.get('news', '<div class="article"><div class="content">No news available today.</div></div>')}
                    </div>
                </section>

                <section class="section">
                    <div class="section-header">
                        <h2>📄 Technology Papers</h2>
                        <span class="toggle-icon">−</span>
                    </div>
                    <div class="section-content expanded">
                        {formatted_content.get('arxiv_papers', '<div class="article"><div class="content">No technology papers available today.</div></div>')}
                    </div>
                </section>

                <section class="section">
                    <div class="section-header">
                        <h2>🏢 Company Papers</h2>
                        <span class="toggle-icon">−</span>
                    </div>
                    <div class="section-content expanded">
                        {formatted_content.get('arxiv_players_papers', '<div class="article"><div class="content">No company papers available today.</div></div>')}
                    </div>
                </section>

                <section class="section">
                    <div class="section-header">
                        <h2>📚 Highlighted Papers</h2>
                        <span class="toggle-icon">−</span>
                    </div>
                    <div class="section-content expanded">
                        {formatted_content.get('research_papers', '<div class="article"><div class="content">No highlighted papers available today.</div></div>')}
                    </div>
                </section>
            </main>

            <footer class="footer">
                <div class="container">
                    <p>Generated automatically by QuantumBoom • Powered by AI</p>
                    <p>Sources: arXiv, Google News, Research Databases</p>
                    <p><em>Updated daily with the latest quantum computing developments</em></p>
                </div>
            </footer>

            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    // Initialize all sections as expanded
                    const sections = document.querySelectorAll('.section');
                    sections.forEach(section => {{
                        const header = section.querySelector('.section-header');
                        const content = section.querySelector('.section-content');
                        const icon = section.querySelector('.toggle-icon');

                        if (header && content && icon) {{
                            // Set initial state (expanded)
                            content.classList.add('expanded');
                            icon.textContent = '−';

                            // Add click handler
                            header.addEventListener('click', function() {{
                                const isExpanded = content.classList.contains('expanded');

                                if (isExpanded) {{
                                    // Collapse
                                    content.classList.remove('expanded');
                                    content.classList.add('collapsed');
                                    icon.textContent = '+';
                                    icon.style.transform = 'rotate(0deg)';
                                }} else {{
                                    // Expand
                                    content.classList.remove('collapsed');
                                    content.classList.add('expanded');
                                    icon.textContent = '−';
                                    icon.style.transform = 'rotate(0deg)';
                                }}
                            }});
                        }}
                    }});

                    // Add expand/collapse all functionality
                    const container = document.querySelector('.container');
                    if (container) {{
                        const toggleAllBtn = document.createElement('button');
                        toggleAllBtn.textContent = 'Collapse All';
                        toggleAllBtn.style.cssText = `
                            position: fixed;
                            top: 20px;
                            right: 20px;
                            background: #00d084;
                            color: white;
                            border: none;
                            padding: 10px 15px;
                            border-radius: 5px;
                            cursor: pointer;
                            font-size: 14px;
                            z-index: 1000;
                            transition: background 0.3s ease;
                        `;

                        toggleAllBtn.addEventListener('mouseenter', function() {{
                            this.style.background = '#00b070';
                        }});

                        toggleAllBtn.addEventListener('mouseleave', function() {{
                            this.style.background = '#00d084';
                        }});

                        toggleAllBtn.addEventListener('click', function() {{
                            const allExpanded = Array.from(sections).every(section =>
                                section.querySelector('.section-content').classList.contains('expanded')
                            );

                            sections.forEach(section => {{
                                const content = section.querySelector('.section-content');
                                const icon = section.querySelector('.toggle-icon');

                                if (allExpanded) {{
                                    // Collapse all
                                    content.classList.remove('expanded');
                                    content.classList.add('collapsed');
                                    icon.textContent = '+';
                                }} else {{
                                    // Expand all
                                    content.classList.remove('collapsed');
                                    content.classList.add('expanded');
                                    icon.textContent = '−';
                                }}
                            }});

                            this.textContent = allExpanded ? 'Expand All' : 'Collapse All';
                        }});

                        document.body.appendChild(toggleAllBtn);
                    }}
                }});
            </script>
        </body>
        </html>
        """

        return html_template

    def create_deploy_folder(self, html_content: str) -> str:
        """Create a deploy folder with the HTML content and return the path."""
        try:
            # Create output/deploy folder structure
            output_folder = Path("output")
            deploy_folder = output_folder / "deploy"

            # Create directories if they don't exist
            output_folder.mkdir(exist_ok=True)
            deploy_folder.mkdir(exist_ok=True)

            # Clear existing files in deploy folder
            for file in deploy_folder.glob("*"):
                if file.is_file():
                    file.unlink()

            # Write the HTML file
            html_file = deploy_folder / "index.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Create a simple _redirects file for Netlify
            redirects_file = deploy_folder / "_redirects"
            with open(redirects_file, 'w') as f:
                f.write("/*    /index.html   200\n")

            # Create a simple robots.txt
            robots_file = deploy_folder / "robots.txt"
            with open(robots_file, 'w') as f:
                f.write("User-agent: *\nAllow: /\n")

            logger.info(f"Deploy folder created at {deploy_folder.absolute()}")
            logger.info(f"Files ready for deployment:")
            for file in deploy_folder.glob("*"):
                logger.info(f"  - {file.name}")

            return str(deploy_folder.absolute())

        except Exception as e:
            logger.error(f"Error creating deploy folder: {str(e)}")
            raise

    def deploy_to_netlify(self, deploy_folder_path: str) -> bool:
        """Deploy the site to Netlify using ZIP file method."""
        try:
            logger.info("Starting Netlify deployment...")

            # Create a temporary ZIP file
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                zip_path = temp_zip.name

            # Create ZIP file from deploy folder
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                deploy_path = Path(deploy_folder_path)
                for file_path in deploy_path.rglob('*'):
                    if file_path.is_file():
                        # Add file to zip with relative path
                        arcname = file_path.relative_to(deploy_path)
                        zipf.write(file_path, arcname)
                        logger.info(f"Added {arcname} to deployment ZIP")

            # Deploy to Netlify
            headers = {
                'Authorization': f"Bearer {self.netlify_config['access_token']}",
                'Content-Type': 'application/zip'
            }

            deploy_url = f"{self.netlify_config['api_base']}/sites/{self.netlify_config['site_id']}/deploys"

            with open(zip_path, 'rb') as zip_file:
                response = requests.post(deploy_url, headers=headers, data=zip_file, timeout=60)

            # Clean up temporary ZIP file
            os.unlink(zip_path)

            if response.status_code in [200, 201]:
                deploy_data = response.json()
                deploy_id = deploy_data.get('id')
                site_url = deploy_data.get('ssl_url') or deploy_data.get('url')

                logger.info(f"✅ Deployment successful!")
                logger.info(f"Deploy ID: {deploy_id}")
                logger.info(f"Site URL: {site_url}")

                # Poll for deployment completion
                self._wait_for_deployment(deploy_id)

                return True
            else:
                logger.error(f"❌ Deployment failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error deploying to Netlify: {str(e)}")
            return False

    def _wait_for_deployment(self, deploy_id: str, max_wait: int = 300):
        """Wait for deployment to complete and report status."""
        try:
            headers = {
                'Authorization': f"Bearer {self.netlify_config['access_token']}"
            }

            check_url = f"{self.netlify_config['api_base']}/deploys/{deploy_id}"
            start_time = time.time()

            while time.time() - start_time < max_wait:
                response = requests.get(check_url, headers=headers)
                if response.status_code == 200:
                    deploy_data = response.json()
                    state = deploy_data.get('state')

                    if state == 'ready':
                        logger.info("🚀 Deployment is live!")
                        return True
                    elif state in ['error', 'failed']:
                        logger.error(f"❌ Deployment failed with state: {state}")
                        return False
                    else:
                        logger.info(f"⏳ Deployment status: {state}")
                        time.sleep(10)  # Wait 10 seconds before checking again
                else:
                    logger.warning(f"Could not check deployment status: {response.status_code}")
                    break

            logger.warning("⚠️ Deployment status check timed out, but deployment may still complete")
            return True

        except Exception as e:
            logger.warning(f"Error checking deployment status: {str(e)}")
            return True  # Don't fail the whole process for status check issues

    def run_daily_digest(self):
        """Main method to run the daily digest process."""
        logger.info("Starting Quantum Computing Daily Digest")
        start_time = time.time()

        try:
            # Fetch all data sources
            logger.info("Fetching data from all sources...")

            # Fetch CSV data
            research_list_df = self.fetch_csv(self.sources['research_list'], 'Research Paper List')
            research_brief_df = self.fetch_csv(self.sources['research_brief'], 'Research Paper Brief')

            # Fetch arXiv papers
            arxiv_papers = self.fetch_arxiv()

            # Fetch arXiv papers from quantum computing players
            arxiv_players_papers = self.fetch_arxiv_players()

            # Fetch news
            news_items = self.fetch_news()

            # Prepare content for formatting
            research_content = []
            if not research_list_df.empty:
                research_content.extend(research_list_df.head(3).to_dict('records'))
            if not research_brief_df.empty:
                research_content.extend(research_brief_df.head(2).to_dict('records'))

            # Format content without GPT
            formatted_content = {}
            stats = {}

            if research_content:
                logger.info("Formatting research papers...")
                formatted_content['research_papers'] = self.format_research_papers(research_content)
                stats['research_papers'] = len(research_content)

            if arxiv_papers:
                logger.info("Formatting latest papers...")
                formatted_content['arxiv_papers'] = self.format_arxiv_papers(arxiv_papers)
                stats['arxiv_papers'] = len(arxiv_papers)

            if arxiv_players_papers:
                logger.info("Formatting quantum computing players papers...")
                formatted_content['arxiv_players_papers'] = self.format_arxiv_players_papers(arxiv_players_papers)
                stats['arxiv_players_papers'] = len(arxiv_players_papers)

            if news_items:
                logger.info("Formatting news items...")
                formatted_content['news'] = self.format_news(news_items)
                stats['news_items'] = len(news_items)

            # Build HTML digest
            logger.info("Building HTML digest")
            html_digest = self.build_html_digest(formatted_content, stats)

            # Create deploy folder
            deploy_folder_path = self.create_deploy_folder(html_digest)

            # Save backup copy in output folder
            output_folder = Path("output")
            output_folder.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = output_folder / f"digest_backup_{timestamp}.html"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                f.write(html_digest)
            logger.info(f"Backup saved to {backup_filename}")

            # Deploy to Netlify
            if self.deploy_to_netlify(deploy_folder_path):
                logger.info("🎉 QuantumBoom deployment completed successfully!")
                logger.info(f"🌐 Your site is live at: https://{self.netlify_config['site_id']}.netlify.app")
            else:
                logger.error("❌ Failed to deploy to Netlify, but digest was generated")

            execution_time = time.time() - start_time
            logger.info(f"Total execution time: {execution_time:.2f} seconds")

        except Exception as e:
            logger.error(f"Error in daily digest process: {str(e)}")
            raise


def main():
    """Main entry point for the script."""
    try:
        digest = QuantumBoom()
        digest.run_daily_digest()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
