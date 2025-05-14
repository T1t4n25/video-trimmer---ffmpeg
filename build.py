"""
Build Script for Video Trimmer Application
Downloads FFmpeg and packages the application
"""

import os
import sys
import platform
import subprocess
import shutil


def check_requirements():
    """Check if all required packages are installed"""
    required_packages = ['PyQt6', 'ffmpeg-python', 'PyInstaller']
    
    # Check each package
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("The following required packages are missing:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def download_ffmpeg():
    """Download and extract FFmpeg"""
    print("Downloading FFmpeg...")
    try:
        # Check if we have write access to temp directory
        temp_dir = os.environ.get('TEMP', os.environ.get('TMP', ''))
        if not os.access(temp_dir, os.W_OK):
            print(f"Error: No write access to temp directory: {temp_dir}")
            return False
            
        # Check if ffmpeg directory exists
        if os.path.exists('ffmpeg'):
            print("FFmpeg directory already exists, skipping download")
            return True
        
        # Run the download_ffmpeg.py script
        python_path = os.environ.get('PYTHON_PATH', sys.executable)
        subprocess.run([python_path, "download_ffmpeg.py"], check=True)
    except subprocess.SubprocessError as e:
        print(f"Error downloading FFmpeg: {str(e)}")
        return False
    except OSError as e:
        print(f"OS Error during FFmpeg download: {str(e)}")
        return False
    
    return True


def build_application():
    """Build the application using PyInstaller"""
    print("Building application with PyInstaller...")
    try:
        # Run PyInstaller with the spec file
        subprocess.run(["pyinstaller", "build_app.spec"], check=True)
    except subprocess.SubprocessError as e:
        print(f"Error building application: {str(e)}")
        return False
    
    return True


def create_distribution():
    """Create a distributable package"""
    dist_dir = "dist/VideoTrimmer"
    
    if not os.path.exists(dist_dir):
        print(f"Error: Build directory {dist_dir} not found")
        return False
    
    # Create a zip file of the distribution
    system = platform.system()
    arch = platform.machine()
    zip_name = f"VideoTrimmer_{system}_{arch}"
    
    print(f"Creating distribution package: {zip_name}.zip")
    
    # Create the zip file
    shutil.make_archive(zip_name, 'zip', os.path.dirname(dist_dir), os.path.basename(dist_dir))
    
    print(f"Distribution package created: {zip_name}.zip")
    return True


def install_upx():
    """Install UPX compression tool"""
    print("Installing UPX...")
    try:
        import urllib.request
        import zipfile
        
        # Download UPX
        upx_url = "https://github.com/upx/upx/releases/download/v4.2.1/upx-4.2.1-win64.zip"
        urllib.request.urlretrieve(upx_url, "upx.zip")
        
        # Extract UPX
        with zipfile.ZipFile("upx.zip", 'r') as zip_ref:
            zip_ref.extractall("upx")
        
        # Add UPX to PATH
        os.environ["PATH"] = os.path.abspath("upx") + os.pathsep + os.environ["PATH"]
        
        # Clean up
        os.remove("upx.zip")
        return True
    except Exception as e:
        print(f"Error installing UPX: {str(e)}")
        return False


def check_env_variables():
    """Check for required environment variables"""
    required_vars = {
        'PYTHON_PATH': os.environ.get('PYTHON_PATH', sys.executable),
        'PATH': os.environ.get('PATH', ''),
        'TEMP': os.environ.get('TEMP', os.environ.get('TMP', '')),
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
        
    # Check if Python is in PATH
    python_dir = os.path.dirname(sys.executable)
    if python_dir not in os.environ['PATH'].split(os.pathsep):
        print("Warning: Python directory not in PATH")
        print(f"Adding {python_dir} to PATH")
        os.environ['PATH'] = python_dir + os.pathsep + os.environ['PATH']
    
    return True


def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        return True
    except subprocess.SubprocessError as e:
        print(f"Error installing requirements: {str(e)}")
        return False


def main():
    """Main build function"""
    print("=== Video Trimmer Build Script ===")
    
    # Install requirements
    print("\nInstalling requirements...")
    if not install_requirements():
        sys.exit(1)
    
    # Check environment variables
    print("\nChecking environment variables...")
    if not check_env_variables():
        print("Please set the required environment variables and try again")
        sys.exit(1)
    
    # Download FFmpeg
    print("\nDownloading FFmpeg...")
    if not download_ffmpeg():
        sys.exit(1)
    
    # Install UPX if not already installed
    if not os.path.exists("upx"):
        if not install_upx():
            sys.exit(1)
    
    # Build the application
    print("\nBuilding application...")
    if not build_application():
        sys.exit(1)
    
    # Create distribution package
    print("\nCreating distribution package...")
    if not create_distribution():
        sys.exit(1)
    
    print("\nBuild completed successfully!")
    print("\nYou can find the application in the 'dist/VideoTrimmer' directory")
    print("A zip package has also been created in the current directory")


if __name__ == "__main__":
    main()