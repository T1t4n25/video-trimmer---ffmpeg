"""
Main script for the Video Trimmer application
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Import application modules
from video_trimmer_gui import VideoTrimmerGUI


def main():
    """
    Main entry point for the application
    """
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("Video Trimmer")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set application icon
    icon_path = os.path.join('icons', 'video_trimmer_2.ico')  # Assuming icon is named app.png
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create and show the main window
    window = VideoTrimmerGUI()
    window.show()
    
    # Execute the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()