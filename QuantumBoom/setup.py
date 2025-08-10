#!/usr/bin/env python3
"""
Setup script for Quantum News Digest
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        sys.exit(1)

def setup_environment():
    """Set up environment configuration."""
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if not env_file.exists():
        if env_template.exists():
            shutil.copy(env_template, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your actual API keys and email configuration")
        else:
            print("❌ .env.template not found")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories."""
    directories = ["logs", "backups"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_cron_example():
    """Create example cron job configuration."""
    cron_example = """
# Example cron job to run Quantum Digest daily at 8:00 AM
# Add this to your crontab with: crontab -e

0 8 * * * cd /path/to/Quantum-news-digest && /usr/bin/python3 quantum_digest.py >> logs/cron.log 2>&1

# Alternative: Run every weekday at 8:00 AM
0 8 * * 1-5 cd /path/to/Quantum-news-digest && /usr/bin/python3 quantum_digest.py >> logs/cron.log 2>&1
"""
    
    with open("cron_example.txt", "w") as f:
        f.write(cron_example)
    print("✅ Created cron_example.txt")

def main():
    """Main setup function."""
    print("🔬 Quantum News Digest Setup")
    print("=" * 40)
    
    check_python_version()
    install_requirements()
    setup_environment()
    create_directories()
    setup_cron_example()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys and email configuration")
    print("2. Test the script: python quantum_digest.py")
    print("3. Set up daily automation using cron (see cron_example.txt)")

if __name__ == "__main__":
    main()
