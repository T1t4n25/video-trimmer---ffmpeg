#!/usr/bin/env python3
"""
Build Script for Video Trimmer Application
Downloads FFmpeg and packages the application
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


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
        # Run the download_ffmpeg.py script
        subprocess.run([sys.executable, "download_ffmpeg.py"], check=True)
    except subprocess.SubprocessError as e:
        print(f"Error downloading FFmpeg: {str(e)}")
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


def main():
    """Main build function"""
    print("=== Video Trimmer Build Script ===")
    
    # Check requirements
    print("\nChecking requirements...")
    if not check_requirements():
        sys.exit(1)
    
    # Download FFmpeg
    print("\nDownloading FFmpeg...")
    if not download_ffmpeg():
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