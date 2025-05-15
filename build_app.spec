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
added_files = [
    (ffmpeg_dir, os.path.join('ffmpeg', 'bin')),
    ('translations', 'translations'),  # Copy translations folder
    ('icons', 'icons')  
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
    strip=True,
    upx=True,
    upx_exclude=[],
    console=False,
    icon='icons/video_trimmer_2.ico',  # Update icon path
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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

# Ensure directories exist at the correct level
build_dir = os.path.join('builds', 'VideoTrimmer')
icons_dir = os.path.join(build_dir, 'icons')
if not os.path.exists(icons_dir):
    os.makedirs(icons_dir)

# Copy entire icons folder to the same level as _internal
icons_src = 'icons'
if os.path.exists(icons_src):
    for file in os.listdir(icons_src):
        src_file = os.path.join(icons_src, file)
        dst_file = os.path.join(icons_dir, file)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dst_file)

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