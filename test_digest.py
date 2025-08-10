#!/usr/bin/env python3
"""
Test script for Quantum News Digest
Tests individual components without sending emails or using API credits extensively.
"""

import os
import sys
from unittest.mock import Mock, patch
import pandas as pd
from quantum_digest import QuantumDigest

def test_environment():
    """Test environment configuration."""
    print("🔧 Testing Environment Configuration")
    
    required_vars = ['OPENAI_API_KEY', 'EMAIL_USER', 'EMAIL_PASSWORD', 'RECIPIENT_EMAIL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"❌ Missing: {var}")
        else:
            print(f"✅ Found: {var}")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        print("Please check your .env file")
        return False
    
    print("✅ Environment configuration is complete")
    return True

def test_data_fetching():
    """Test data fetching capabilities."""
    print("\n📡 Testing Data Fetching")
    
    try:
        digest = QuantumDigest()
        
        # Test CSV fetching
        print("Testing CSV fetch...")
        test_df = digest.fetch_csv(digest.sources['research_list'], 'Test Research List')
        if not test_df.empty:
            print(f"✅ CSV fetch successful: {len(test_df)} rows")
        else:
            print("⚠️  CSV fetch returned empty DataFrame")
        
        # Test arXiv fetching
        print("Testing arXiv fetch...")
        arxiv_papers = digest.fetch_arxiv()
        if arxiv_papers:
            print(f"✅ arXiv fetch successful: {len(arxiv_papers)} papers")
            print(f"   Sample title: {arxiv_papers[0]['title'][:60]}...")
        else:
            print("⚠️  arXiv fetch returned no papers")
        
        # Test news fetching
        print("Testing news fetch...")
        news_items = digest.fetch_news()
        if news_items:
            print(f"✅ News fetch successful: {len(news_items)} items")
            print(f"   Sample headline: {news_items[0]['title'][:60]}...")
        else:
            print("⚠️  News fetch returned no items")
        
        return True
        
    except Exception as e:
        print(f"❌ Data fetching failed: {str(e)}")
        return False

def test_gpt_summarization():
    """Test GPT summarization with mock data."""
    print("\n🤖 Testing GPT Summarization")
    
    try:
        digest = QuantumDigest()
        
        # Create mock data
        mock_papers = [
            {
                'title': 'Quantum Error Correction in NISQ Devices',
                'authors': 'Smith, J. et al.',
                'abstract': 'This paper presents a novel approach to quantum error correction suitable for near-term quantum devices. We demonstrate improved fidelity through adaptive protocols.'
            }
        ]
        
        mock_news = [
            {
                'title': 'IBM Announces 1000-Qubit Quantum Processor',
                'source': 'TechCrunch',
                'published': '2024-01-15'
            }
        ]
        
        # Test research paper summarization
        print("Testing research paper summarization...")
        research_summary = digest.summarize_with_gpt(mock_papers, 'research_papers')
        if research_summary and len(research_summary) > 50:
            print("✅ Research paper summarization successful")
            print(f"   Summary length: {len(research_summary)} characters")
        else:
            print("⚠️  Research paper summarization may have issues")
        
        # Test news summarization
        print("Testing news summarization...")
        news_summary = digest.summarize_with_gpt(mock_news, 'news')
        if news_summary and len(news_summary) > 30:
            print("✅ News summarization successful")
            print(f"   Summary length: {len(news_summary)} characters")
        else:
            print("⚠️  News summarization may have issues")
        
        return True
        
    except Exception as e:
        print(f"❌ GPT summarization failed: {str(e)}")
        print("   This might be due to API key issues or rate limits")
        return False

def test_html_generation():
    """Test HTML digest generation."""
    print("\n📄 Testing HTML Generation")
    
    try:
        digest = QuantumDigest()
        
        # Mock summaries
        mock_summaries = {
            'research_papers': '<h4>Test Paper</h4><p>This is a test summary.</p>',
            'arxiv_papers': '<h4>arXiv Paper</h4><p>This is an arXiv summary.</p>',
            'news': '<h4>Test News</h4><p>This is a news summary.</p>'
        }
        
        html_content = digest.build_html_digest(mock_summaries)
        
        # Basic HTML validation
        if '<html>' in html_content and '</html>' in html_content:
            print("✅ HTML structure is valid")
        else:
            print("❌ HTML structure is invalid")
            return False
        
        # Check for required sections
        required_sections = ['Research Paper Highlights', 'Latest arXiv Papers', 'Recent News']
        for section in required_sections:
            if section in html_content:
                print(f"✅ Found section: {section}")
            else:
                print(f"❌ Missing section: {section}")
                return False
        
        # Save test HTML
        with open('test_digest.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ Test HTML saved as 'test_digest.html'")
        
        return True
        
    except Exception as e:
        print(f"❌ HTML generation failed: {str(e)}")
        return False

def test_email_config():
    """Test email configuration without sending."""
    print("\n📧 Testing Email Configuration")
    
    try:
        digest = QuantumDigest()
        
        # Check email configuration
        email_config = digest.email_config
        
        if email_config['email_user'] and email_config['email_password']:
            print("✅ Email credentials configured")
        else:
            print("❌ Email credentials missing")
            return False
        
        if email_config['recipient_email']:
            print("✅ Recipient email configured")
        else:
            print("❌ Recipient email missing")
            return False
        
        print(f"✅ SMTP server: {email_config['smtp_server']}:{email_config['smtp_port']}")
        print("⚠️  Email sending not tested (use main script to test actual sending)")
        
        return True
        
    except Exception as e:
        print(f"❌ Email configuration test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🔬 Quantum News Digest - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Data Fetching", test_data_fetching),
        ("GPT Summarization", test_gpt_summarization),
        ("HTML Generation", test_html_generation),
        ("Email Configuration", test_email_config)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Ready to run the main digest.")
    else:
        print("\n⚠️  Some tests failed. Please check configuration and try again.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
