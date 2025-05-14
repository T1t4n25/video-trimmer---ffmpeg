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

# Define paths for bundled ffmpeg
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
added_files = ffmpeg_files

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['PyQt6', 'ffmpeg'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
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
    strip=False,
    upx=True,
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