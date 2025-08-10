#!/usr/bin/env python3
"""
Quantum News Digest - No-GPT Preview Mode
Generates the HTML digest with raw data formatting (no AI summarization) for preview.
"""

import os
import sys
import logging
import pandas as pd
import feedparser
import requests
from datetime import datetime
from typing import List, Dict
import time
import webbrowser
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantum_digest_no_gpt.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class QuantumDigestNoGPT:
    def __init__(self):
        """Initialize the Quantum Digest Preview without GPT."""
        # Data source URLs
        self.sources = {
            'research_list': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTjka1LpVvM74sNMqcZCxh0WsQXi8IUbIknLEojpmSysEeQUG2BStQNGwdgKD9Q9jkzAAtDmcMrLYG5/pub?output=csv',
            'research_brief': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQQGTFKG6AKhJVLBujShiHC6vtQ9gbN5TSnrcEqzElOsCJTkRdPYXNThJJQNhHSY68Z0-zfiJffhz64/pub?output=csv',
            'arxiv_api': 'https://export.arxiv.org/api/query?search_query=ti:%22quantum%20computing%22&sortBy=lastUpdatedDate&sortOrder=descending&max_results=8',
            'google_news': 'https://news.google.com/rss/search?q=quantum+computing'
        }
        
        logger.info("Quantum Digest No-GPT Preview initialized successfully")

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
            for entry in feed.entries[:6]:  # Limit to 6 for preview
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

    def fetch_news(self) -> List[Dict]:
        """Fetch latest quantum computing news from Google News."""
        try:
            logger.info("Fetching Google News")
            feed = feedparser.parse(self.sources['google_news'])
            
            news_items = []
            for entry in feed.entries[:10]:  # Limit to 10 for preview
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
            return "<p>No research papers available today.</p>"

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
            date_info = f" • <em>Submitted: {submission_date[:10]}</em>" if submission_date and str(submission_date) != 'nan' else ""
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
            return "<p>No arXiv papers available today.</p>"
        
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

    def format_news(self, news_items: List[Dict]) -> str:
        """Format news items without GPT."""
        if not news_items:
            return "<p>No news available today.</p>"
        
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

    def build_html_digest(self, formatted_content: Dict[str, str], stats: Dict[str, int]) -> str:
        """Build the complete HTML digest for preview."""
        current_date = datetime.now().strftime("%B %d, %Y")

        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Quantum Computing Digest - {current_date}</title>
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

                .preview-notice {{
                    background: #f0f8ff;
                    border-left: 4px solid #0066cc;
                    padding: 16px 20px;
                    margin-bottom: 40px;
                    font-size: 0.95rem;
                    color: #0066cc;
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

                .section h2 {{
                    font-size: 1.8rem;
                    font-weight: 700;
                    color: #1a1a1a;
                    margin-bottom: 24px;
                    letter-spacing: -0.01em;
                    border-bottom: 2px solid #00d084;
                    padding-bottom: 8px;
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
                    <div class="subtitle">Daily Research & News Summary • {current_date}</div>
                </div>
            </header>

            <main class="container">
                <div class="preview-notice">
                    <strong>📋 Preview Mode:</strong> This shows raw data formatting without AI summarization.
                    Once OpenAI quota is restored, you'll get intelligent GPT summaries.
                </div>

                <div class="stats">
                    <h3>📊 Today's Data Collection</h3>
                    <p>
                        <strong>Research Papers:</strong> {stats.get('research_papers', 0)} papers collected<br>
                        <strong>arXiv Papers:</strong> {stats.get('arxiv_papers', 0)} papers fetched<br>
                        <strong>News Items:</strong> {stats.get('news_items', 0)} articles gathered<br>
                        <strong>Total Sources:</strong> 4 data feeds processed
                    </p>
                </div>

                <section class="section">
                    <h2>📚 Research Paper Highlights</h2>
                    {formatted_content.get('research_papers', '<div class="article"><div class="content">No research papers available today.</div></div>')}
                </section>

                <section class="section">
                    <h2>📄 Latest arXiv Papers</h2>
                    {formatted_content.get('arxiv_papers', '<div class="article"><div class="content">No arXiv papers available today.</div></div>')}
                </section>

                <section class="section">
                    <h2>📰 Recent News & Developments</h2>
                    {formatted_content.get('news', '<div class="article"><div class="content">No news available today.</div></div>')}
                </section>
            </main>

            <footer class="footer">
                <div class="container">
                    <p>Generated automatically by Quantum Digest • Powered by AI</p>
                    <p>Sources: arXiv, Google News, Research Databases</p>
                    <p><em>Preview Mode - Add OpenAI credits for intelligent summaries</em></p>
                </div>
            </footer>
        </body>
        </html>
        """

        return html_template

    def run_preview(self):
        """Main method to run the no-GPT preview digest process."""
        logger.info("Starting Quantum Computing Digest No-GPT Preview")
        start_time = time.time()

        try:
            # Fetch all data sources
            logger.info("Fetching data from all sources...")

            # Fetch CSV data
            research_list_df = self.fetch_csv(self.sources['research_list'], 'Research Paper List')
            research_brief_df = self.fetch_csv(self.sources['research_brief'], 'Research Paper Brief')

            # Fetch arXiv papers
            arxiv_papers = self.fetch_arxiv()

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
                logger.info("Formatting arXiv papers...")
                formatted_content['arxiv_papers'] = self.format_arxiv_papers(arxiv_papers)
                stats['arxiv_papers'] = len(arxiv_papers)

            if news_items:
                logger.info("Formatting news items...")
                formatted_content['news'] = self.format_news(news_items)
                stats['news_items'] = len(news_items)

            # Build HTML digest
            logger.info("Building HTML digest preview")
            html_digest = self.build_html_digest(formatted_content, stats)

            # Save digest to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            preview_filename = f"quantum_digest_no_gpt_{timestamp}.html"
            with open(preview_filename, 'w', encoding='utf-8') as f:
                f.write(html_digest)

            logger.info(f"No-GPT preview digest saved to {preview_filename}")

            # Try to open in browser
            try:
                import os
                full_path = os.path.abspath(preview_filename)
                webbrowser.open(f'file://{full_path}')
                logger.info("Preview opened in browser")
            except Exception as e:
                logger.warning(f"Could not open browser: {e}")
                logger.info(f"Please open {preview_filename} manually in your browser")

            execution_time = time.time() - start_time
            logger.info(f"No-GPT preview generation completed in {execution_time:.2f} seconds")

            print(f"\n🎉 No-GPT preview digest generated successfully!")
            print(f"📁 File saved as: {preview_filename}")
            print(f"🌐 Opening in browser...")
            print(f"\n💡 This shows the raw data structure. Once OpenAI quota is restored,")
            print(f"   the full version will include intelligent GPT summaries!")

        except Exception as e:
            logger.error(f"Error in no-GPT preview digest process: {str(e)}")
            raise


def main():
    """Main entry point for the no-GPT preview script."""
    try:
        print("🚀 QuantumBoom - No-GPT Preview Mode")
        print("=" * 55)

        digest = QuantumDigestNoGPT()
        digest.run_preview()

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        print("Check quantum_digest_no_gpt.log for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
