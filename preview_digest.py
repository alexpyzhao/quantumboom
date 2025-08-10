#!/usr/bin/env python3
"""
Quantum News Digest - Preview Mode
Generates the HTML digest and saves it locally for preview without email setup.
"""

import os
import sys
import logging
import pandas as pd
import feedparser
import requests
from datetime import datetime
from openai import OpenAI
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
        logging.FileHandler('quantum_digest_preview.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class QuantumDigestPreview:
    def __init__(self):
        """Initialize the Quantum Digest Preview with minimal configuration."""
        # Check for OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            logger.info("Please set your OpenAI API key in the .env file")
            sys.exit(1)
        
        self.openai_client = OpenAI(api_key=api_key)
        
        # Data source URLs
        self.sources = {
            'research_list': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTjka1LpVvM74sNMqcZCxh0WsQXi8IUbIknLEojpmSysEeQUG2BStQNGwdgKD9Q9jkzAAtDmcMrLYG5/pub?output=csv',
            'research_brief': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQQGTFKG6AKhJVLBujShiHC6vtQ9gbN5TSnrcEqzElOsCJTkRdPYXNThJJQNhHSY68Z0-zfiJffhz64/pub?output=csv',
            'arxiv_api': 'https://export.arxiv.org/api/query?search_query=ti:%22quantum%20computing%22&sortBy=lastUpdatedDate&sortOrder=descending&max_results=10',
            'google_news': 'https://news.google.com/rss/search?q=quantum+computing'
        }
        
        logger.info("Quantum Digest Preview initialized successfully")

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
            for entry in feed.entries[:5]:  # Limit to 5 for preview
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
            for entry in feed.entries[:8]:  # Limit to 8 for preview
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

    def summarize_with_gpt(self, content_list: List[Dict], context: str) -> str:
        """Use GPT to summarize content intelligently based on context."""
        if not content_list:
            return "<p>No content available for summarization.</p>"
        
        try:
            # Prepare content for GPT
            content_text = self._prepare_content_for_gpt(content_list, context)
            
            # Create context-specific prompt
            prompt = self._create_summarization_prompt(context)
            
            logger.info(f"Sending {len(content_list)} items to GPT for {context} summarization")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content_text}
                ],
                max_tokens=1500,  # Reduced for preview
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            logger.info(f"Successfully generated {context} summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error in GPT summarization for {context}: {str(e)}")
            return f"<p>Error generating summary for {context}: {str(e)}</p>"

    def _prepare_content_for_gpt(self, content_list: List[Dict], context: str) -> str:
        """Prepare content for GPT based on context type."""
        if context == "research_papers":
            return "\n\n".join([
                f"Title: {item.get('title', 'N/A')}\n"
                f"Authors: {item.get('authors', 'N/A')}\n"
                f"Abstract: {item.get('abstract', 'N/A')[:400]}..."
                for item in content_list[:3]  # Limit for preview
            ])
        elif context == "arxiv_papers":
            return "\n\n".join([
                f"Title: {item['title']}\n"
                f"Authors: {item['authors']}\n"
                f"Abstract: {item['abstract'][:400]}..."
                for item in content_list
            ])
        elif context == "news":
            return "\n\n".join([
                f"Headline: {item['title']}\n"
                f"Source: {item.get('source', 'Unknown')}\n"
                f"Published: {item.get('published', 'N/A')}"
                for item in content_list
            ])
        else:
            return str(content_list)

    def _create_summarization_prompt(self, context: str) -> str:
        """Create context-specific prompts for GPT summarization."""
        base_instructions = """You are an expert quantum computing researcher and science communicator. 
        Your task is to create concise, insightful summaries that highlight the most important information."""
        
        if context == "research_papers" or context == "arxiv_papers":
            return f"""{base_instructions}
            
            For research papers, focus on:
            - Key findings and novel contributions
            - Methodology innovations or improvements
            - Practical implications for quantum computing
            - Potential impact on the field
            
            Format as HTML with:
            - Use <h4> for paper titles
            - Use <p> for 2-3 sentence summaries
            - Use <ul><li> for key points when appropriate
            - Include author names in italics
            - Avoid boilerplate phrases like "This paper explores"
            
            Keep each summary to 3-4 sentences maximum."""
            
        elif context == "news":
            return f"""{base_instructions}
            
            For news items, focus on:
            - Major announcements or breakthroughs
            - Market impacts and business developments
            - Policy or regulatory changes
            - Significant partnerships or investments
            
            Format as HTML with:
            - Use <h4> for headlines
            - Use <p> for 1-2 sentence summaries
            - Group related stories when possible
            - Highlight the source in <em> tags
            - Focus on actionable insights
            
            Keep each summary to 2-3 sentences maximum."""
            
        else:
            return f"{base_instructions}\n\nProvide a concise HTML summary of the content."

    def build_html_digest(self, summaries: Dict[str, str]) -> str:
        """Build the complete HTML digest for preview."""
        current_date = datetime.now().strftime("%B %d, %Y")

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Quantum Computing Digest - {current_date} (Preview)</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 1.1em;
                }}
                .preview-notice {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 25px;
                    text-align: center;
                }}
                .section {{
                    background: white;
                    margin-bottom: 25px;
                    padding: 25px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .section h2 {{
                    color: #667eea;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                    margin-top: 0;
                    font-size: 1.8em;
                }}
                .section h4 {{
                    color: #444;
                    margin-top: 20px;
                    margin-bottom: 10px;
                    font-size: 1.2em;
                }}
                .section p {{
                    margin-bottom: 15px;
                    text-align: justify;
                }}
                .section ul {{
                    margin-bottom: 15px;
                }}
                .section li {{
                    margin-bottom: 5px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 0.9em;
                    border-top: 1px solid #ddd;
                    margin-top: 30px;
                }}
                em {{
                    color: #667eea;
                    font-style: normal;
                    font-weight: 600;
                }}
                a {{
                    color: #667eea;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .stats {{
                    background: #e3f2fd;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .stats h3 {{
                    margin-top: 0;
                    color: #1976d2;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔬 Quantum Computing Digest</h1>
                <p>Daily Research & News Summary • {current_date}</p>
            </div>

            <div class="preview-notice">
                <strong>📋 Preview Mode</strong> - This is a preview of your daily digest.
                Configure email settings to receive this automatically.
            </div>

            <div class="stats">
                <h3>📊 Today's Summary</h3>
                <p>
                    <strong>Research Papers:</strong> {len(summaries.get('research_papers', '').split('<h4>')) - 1 if summaries.get('research_papers') else 0} papers analyzed<br>
                    <strong>arXiv Papers:</strong> {len(summaries.get('arxiv_papers', '').split('<h4>')) - 1 if summaries.get('arxiv_papers') else 0} papers summarized<br>
                    <strong>News Items:</strong> {len(summaries.get('news', '').split('<h4>')) - 1 if summaries.get('news') else 0} articles reviewed
                </p>
            </div>

            <div class="section">
                <h2>📚 Research Paper Highlights</h2>
                {summaries.get('research_papers', '<p>No research papers available today.</p>')}
            </div>

            <div class="section">
                <h2>📄 Latest arXiv Papers</h2>
                {summaries.get('arxiv_papers', '<p>No arXiv papers available today.</p>')}
            </div>

            <div class="section">
                <h2>📰 Recent News & Developments</h2>
                {summaries.get('news', '<p>No news available today.</p>')}
            </div>

            <div class="footer">
                <p>Generated automatically by Quantum Digest • Powered by GPT-4</p>
                <p>Sources: arXiv, Google News, Research Databases</p>
                <p><em>Preview Mode - Configure email to receive daily digests</em></p>
            </div>
        </body>
        </html>
        """

        return html_template

    def run_preview(self):
        """Main method to run the preview digest process."""
        logger.info("Starting Quantum Computing Digest Preview")
        start_time = time.time()

        try:
            # Fetch all data sources
            logger.info("Fetching data from all sources...")

            # Fetch CSV data (limited for preview)
            research_list_df = self.fetch_csv(self.sources['research_list'], 'Research Paper List')
            research_brief_df = self.fetch_csv(self.sources['research_brief'], 'Research Paper Brief')

            # Fetch arXiv papers
            arxiv_papers = self.fetch_arxiv()

            # Fetch news
            news_items = self.fetch_news()

            # Prepare content for summarization
            summaries = {}

            # Summarize research papers (combine both CSV sources, limit for preview)
            research_content = []
            if not research_list_df.empty:
                research_content.extend(research_list_df.head(2).to_dict('records'))  # Limit to 2
            if not research_brief_df.empty:
                research_content.extend(research_brief_df.head(2).to_dict('records'))  # Limit to 2

            if research_content:
                logger.info("Generating research paper summaries...")
                summaries['research_papers'] = self.summarize_with_gpt(research_content, 'research_papers')

            # Summarize arXiv papers
            if arxiv_papers:
                logger.info("Generating arXiv paper summaries...")
                summaries['arxiv_papers'] = self.summarize_with_gpt(arxiv_papers, 'arxiv_papers')

            # Summarize news
            if news_items:
                logger.info("Generating news summaries...")
                summaries['news'] = self.summarize_with_gpt(news_items, 'news')

            # Build HTML digest
            logger.info("Building HTML digest preview")
            html_digest = self.build_html_digest(summaries)

            # Save digest to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            preview_filename = f"quantum_digest_preview_{timestamp}.html"
            with open(preview_filename, 'w', encoding='utf-8') as f:
                f.write(html_digest)

            logger.info(f"Preview digest saved to {preview_filename}")

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
            logger.info(f"Preview generation completed in {execution_time:.2f} seconds")

            print(f"\n🎉 Preview digest generated successfully!")
            print(f"📁 File saved as: {preview_filename}")
            print(f"🌐 Opening in browser...")

        except Exception as e:
            logger.error(f"Error in preview digest process: {str(e)}")
            raise


def main():
    """Main entry point for the preview script."""
    try:
        print("🔬 Quantum Computing Digest - Preview Mode")
        print("=" * 50)

        digest = QuantumDigestPreview()
        digest.run_preview()

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        print("Check quantum_digest_preview.log for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
