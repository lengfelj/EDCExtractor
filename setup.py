#!/usr/bin/env python3
"""
Setup script for EHR to EDC POC
"""

import subprocess
import sys
import os


def setup_project():
    """Setup the project environment"""
    
    print("🚀 Setting up EHR to EDC POC...")
    
    # Install dependencies
    print("\n📦 Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Install Playwright browsers
    print("\n🌐 Installing Playwright browsers...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    # Check for .env file
    if not os.path.exists(".env"):
        print("\n⚠️  No .env file found. Creating from template...")
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✓ Created .env file. Please add your API keys.")
        else:
            print("❌ .env.example not found!")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Add your OpenAI API key to .env file")
    print("2. Run the demo with: streamlit run src/main.py")
    print("3. Or test with: python test_extraction.py <document_path>")


if __name__ == "__main__":
    setup_project()