# PyInstaller Specification File for Video Trimmer
# Usage: pyinstaller build_app.spec

import os
import platform
import sys
import shutil
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Determine system
system = platform.system()

# Define paths for bundled ffmpeg and other resources
if system == "Windows":
    ffmpeg_dir = os.path.join('ffmpeg', 'bin')
    ffmpeg_files = [(os.path.join(ffmpeg_dir, file), os.path.join('ffmpeg', 'bin', file)) 
                    for file in ['ffmpeg.exe', 'ffprobe.exe']]
elif system == "Darwin":  # macOS
    ffmpeg_dir = 'ffmpeg'
    ffmpeg_files = [(os.path.join(ffmpeg_dir, file), os.path.join('ffmpeg', file)) 
                    for file in ['ffmpeg', 'ffprobe']]
else:  # Linux
    ffmpeg_dir = 'ffmpeg'
    ffmpeg_files = [(os.path.join(ffmpeg_dir, file), os.path.join('ffmpeg', file)) 
                    for file in ['ffmpeg', 'ffprobe']]

# Get additional data files
added_files = ffmpeg_files + [
    ('icons', 'icons'),  # Copy entire icons folder
    ('translations', 'translations')  # Copy entire translations folder
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['PyQt6', 'ffmpeg'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'notebook', 'PIL', 'pandas', 'numpy', 
        'tk', 'tkinter', 'scipy', 'email', 'html', 'xml',
        'pkg_resources', 'docutils'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    distpath=os.path.join(os.getcwd(), 'builds'),  # Set output directory to 'builds'
    workpath=os.path.join(os.getcwd(), 'builds', 'build')  # Set work directory
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoTrimmer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip symbols from binaries
    upx=True,    # Enable UPX compression
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico' if os.path.exists('app_icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoTrimmer',
)

# Create builds directory if it doesn't exist
if not os.path.exists('builds'):
    os.makedirs('builds')

# For macOS, create a .app bundle
if system == "Darwin":
    app = BUNDLE(
        coll,
        name='VideoTrimmer.app',
        icon='app_icon.icns' if os.path.exists('app_icon.icns') else None,
        bundle_identifier=None,
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
        },
    )