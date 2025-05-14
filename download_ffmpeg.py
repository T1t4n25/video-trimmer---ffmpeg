#!/usr/bin/env python3
"""
Download FFmpeg script - downloads the appropriate FFmpeg binaries for the current platform
"""

import os
import platform
import shutil
import subprocess
import sys
import zipfile
import tarfile
import tempfile
from urllib.request import urlretrieve
from pathlib import Path

# URLs for each platform
FFMPEG_URLS = {
    'Windows': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
    'Darwin': 'https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip',  # macOS
    'Linux': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'  # Linux (amd64)
}

# Directory to extract files to
FFMPEG_DIR = 'ffmpeg'


def get_ffmpeg_url():
    """Get the appropriate FFmpeg URL for the current platform."""
    system = platform.system()
    if system not in FFMPEG_URLS:
        print(f"Unsupported platform: {system}")
        sys.exit(1)
    return FFMPEG_URLS[system]


def download_file(url, output_file):
    """Download a file from a URL to a local file."""
    print(f"Downloading FFmpeg from {url}...")
    try:
        urlretrieve(url, output_file)
        print(f"Downloaded to {output_file}")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        sys.exit(1)


def extract_windows_ffmpeg(zip_file):
    """Extract FFmpeg from the Windows zip file."""
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extract zip file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the bin directory (structure: ffmpeg-xxxx-xxxx/bin/)
        bin_dirs = []
        for root, dirs, files in os.walk(temp_dir):
            for dir_name in dirs:
                if dir_name == 'bin':
                    bin_path = os.path.join(root, dir_name)
                    if os.path.isfile(os.path.join(bin_path, 'ffmpeg.exe')):
                        bin_dirs.append(bin_path)
        
        if not bin_dirs:
            print("Could not find FFmpeg binaries in the downloaded archive")
            sys.exit(1)
        
        # Use the first valid bin directory found
        bin_dir = bin_dirs[0]
        
        # Create target directory
        os.makedirs(os.path.join(FFMPEG_DIR, 'bin'), exist_ok=True)
        
        # Copy necessary files
        shutil.copy2(os.path.join(bin_dir, 'ffmpeg.exe'), os.path.join(FFMPEG_DIR, 'bin'))
        shutil.copy2(os.path.join(bin_dir, 'ffprobe.exe'), os.path.join(FFMPEG_DIR, 'bin'))
        
        print(f"FFmpeg extracted to {FFMPEG_DIR}/bin")
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def extract_macos_ffmpeg(zip_file):
    """Extract FFmpeg from the macOS zip file."""
    # Create ffmpeg directory
    os.makedirs(FFMPEG_DIR, exist_ok=True)
    
    # Extract the zip file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(FFMPEG_DIR)
    
    # Also download ffprobe
    ffprobe_url = 'https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip'
    ffprobe_zip = os.path.join(tempfile.gettempdir(), 'ffprobe.zip')
    
    try:
        download_file(ffprobe_url, ffprobe_zip)
        with zipfile.ZipFile(ffprobe_zip, 'r') as zip_ref:
            zip_ref.extractall(FFMPEG_DIR)
        
        # Make executables... executable
        os.chmod(os.path.join(FFMPEG_DIR, 'ffmpeg'), 0o755)
        os.chmod(os.path.join(FFMPEG_DIR, 'ffprobe'), 0o755)
        
        print(f"FFmpeg extracted to {FFMPEG_DIR}")
    
    finally:
        # Clean up
        if os.path.exists(ffprobe_zip):
            os.remove(ffprobe_zip)


def extract_linux_ffmpeg(tar_file):
    """Extract FFmpeg from the Linux tar.xz file."""
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extract tar file
        with tarfile.open(tar_file, 'r:xz') as tar_ref:
            tar_ref.extractall(temp_dir)
        
        # Find the ffmpeg and ffprobe binaries
        ffmpeg_path = None
        ffprobe_path = None
        
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file == 'ffmpeg':
                    ffmpeg_path = os.path.join(root, file)
                elif file == 'ffprobe':
                    ffprobe_path = os.path.join(root, file)
        
        if not ffmpeg_path or not ffprobe_path:
            print("Could not find FFmpeg/FFprobe binaries in the downloaded archive")
            sys.exit(1)
        
        # Create target directory
        os.makedirs(FFMPEG_DIR, exist_ok=True)
        
        # Copy necessary files
        shutil.copy2(ffmpeg_path, FFMPEG_DIR)
        shutil.copy2(ffprobe_path, FFMPEG_DIR)
        
        # Make executables... executable
        os.chmod(os.path.join(FFMPEG_DIR, 'ffmpeg'), 0o755)
        os.chmod(os.path.join(FFMPEG_DIR, 'ffprobe'), 0o755)
        
        print(f"FFmpeg extracted to {FFMPEG_DIR}")
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def main():
    """Main function to download and extract FFmpeg."""
    # Get URL for current platform
    url = get_ffmpeg_url()
    
    # Get system
    system = platform.system()
    
    # Create temporary file for the download
    temp_file = tempfile.NamedTemporaryFile(delete=False).name
    
    try:
        # Download the file
        download_file(url, temp_file)
        
        # Extract based on platform
        if system == 'Windows':
            extract_windows_ffmpeg(temp_file)
        elif system == 'Darwin':  # macOS
            extract_macos_ffmpeg(temp_file)
        elif system == 'Linux':
            extract_linux_ffmpeg(temp_file)
        else:
            print(f"Unsupported platform: {system}")
            sys.exit(1)
        
        print("FFmpeg has been downloaded and extracted successfully!")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    main()