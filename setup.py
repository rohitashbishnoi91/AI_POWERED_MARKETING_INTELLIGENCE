"""
Setup script for AI-Powered Market Intelligence System
"""

import os
import subprocess
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        'data/raw',
        'data/processed', 
        'reports',
        'outputs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python dependencies...")
    
    # Try to upgrade pip first
    try:
        print("🔄 Upgrading pip...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        print("✅ Pip upgraded successfully")
    except subprocess.CalledProcessError:
        print("⚠️ Could not upgrade pip, continuing with current version...")
    
    # Install requirements with user flag to avoid permission issues
    try:
        print("📦 Installing core dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install with --user flag: {e}")
        
        # Try without user flag
        try:
            print("🔄 Retrying without --user flag...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"❌ Failed to install dependencies: {e2}")
            print("\n🔧 Manual installation instructions:")
            print("1. Open Command Prompt as Administrator")
            print("2. Run: pip install --upgrade pip")
            print("3. Run: pip install -r requirements.txt")
            print("4. Or install packages individually:")
            print("   pip install pandas numpy requests google-generativeai streamlit plotly")
            return False

def create_env_file():
    """Create .env file from template"""
    env_file = Path('.env')
    env_example = Path('env_example.txt')
    
    if not env_file.exists() and env_example.exists():
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from template")
        print("⚠️  Please add your API keys to the .env file:")
        print("   - GEMINI_API_KEY (required for AI insights)")
        print("   - RAPIDAPI_KEY (optional for App Store data)")
    else:
        print("ℹ️  .env file already exists")

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor} is compatible")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up AI-Powered Market Intelligence System")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create directories
    print("\n📁 Creating project directories...")
    create_directories()
    
    # Install requirements
    print("\n📦 Installing dependencies...")
    if not install_requirements():
        print("❌ Setup failed during dependency installation")
        return
    
    # Create .env file
    print("\n🔐 Setting up configuration...")
    create_env_file()
    
    print("\n✅ Setup completed successfully!")
    print("\n🎯 Next steps:")
    print("1. Add your API keys to the .env file")
    print("2. Download the Kaggle dataset or run demo mode:")
    print("   python main.py demo")
    print("3. Run the full pipeline:")
    print("   python main.py pipeline --data data/raw/googleplaystore.csv")
    print("4. Launch the interface:")
    print("   python main.py interface --interface streamlit")
    
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
