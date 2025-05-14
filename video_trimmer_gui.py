#!/usr/bin/env python3
"""
Video Trimmer GUI - A PyQt6 application for trimming video files
"""

import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QListWidget, QCheckBox,
    QDoubleSpinBox, QMessageBox, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

# Import video processor module
from video_processor import VideoProcessor


class VideoTrimmerGUI(QMainWindow):
    """Main window class for the Video Trimmer application"""
    
    def __init__(self):
        super().__init__()
        self.video_processor = VideoProcessor()
        self.selected_files = []
        self.setWindowTitle("Video Trimmer")
        self.resize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # File selection section
        self.setup_file_selection(main_layout)
        
        # Trimming options section
        self.setup_trimming_options(main_layout)
        
        # Progress section
        self.setup_progress_section(main_layout)
        
        # Buttons section
        self.setup_buttons(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def setup_file_selection(self, main_layout):
        """Set up the file selection section of the GUI"""
        # File selection section
        file_section = QFrame()
        file_section.setFrameShape(QFrame.Shape.StyledPanel)
        file_layout = QVBoxLayout(file_section)
        
        # Header
        header = QLabel("Video Files")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        file_layout.addWidget(header)
        
        # File selection buttons
        btn_layout = QHBoxLayout()
        
        self.select_btn = QPushButton("Select Video Files")
        self.select_btn.clicked.connect(self.select_files)
        btn_layout.addWidget(self.select_btn)
        
        self.clear_btn = QPushButton("Clear Selection")
        self.clear_btn.clicked.connect(self.clear_selection)
        btn_layout.addWidget(self.clear_btn)
        
        file_layout.addLayout(btn_layout)
        
        # File list
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)
        
        main_layout.addWidget(file_section)
    
    def setup_trimming_options(self, main_layout):
        """Set up the trimming options section of the GUI"""
        # Trimming options section
        trim_section = QFrame()
        trim_section.setFrameShape(QFrame.Shape.StyledPanel)
        trim_layout = QVBoxLayout(trim_section)
        
        # Header
        header = QLabel("Trimming Options")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        trim_layout.addWidget(header)
        
        # Start time
        start_layout = QHBoxLayout()
        start_label = QLabel("Start Time (seconds):")
        start_layout.addWidget(start_label)
        
        self.start_time = QDoubleSpinBox()
        self.start_time.setMinimum(0)
        self.start_time.setMaximum(3600 * 10)  # 10 hours max
        self.start_time.setValue(0)
        self.start_time.setDecimals(2)
        start_layout.addWidget(self.start_time)
        
        trim_layout.addLayout(start_layout)
        
        # End time
        end_layout = QHBoxLayout()
        end_label = QLabel("End Time (seconds):")
        end_layout.addWidget(end_label)
        
        self.end_time = QDoubleSpinBox()
        self.end_time.setMinimum(0)
        self.end_time.setMaximum(3600 * 10)  # 10 hours max
        self.end_time.setValue(60)
        self.end_time.setDecimals(2)
        end_layout.addWidget(self.end_time)
        
        trim_layout.addLayout(end_layout)
        
        # Option to use end of video
        self.use_end_of_video = QCheckBox("Use End of Video")
        self.use_end_of_video.setChecked(False)
        self.use_end_of_video.stateChanged.connect(self.toggle_end_time)
        trim_layout.addWidget(self.use_end_of_video)
        
        main_layout.addWidget(trim_section)
    
    def setup_progress_section(self, main_layout):
        """Set up the progress section of the GUI"""
        # Progress section
        progress_section = QFrame()
        progress_layout = QVBoxLayout(progress_section)
        
        # Progress bar
        self.progress_label = QLabel("Progress:")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        # Status message
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        main_layout.addWidget(progress_section)
    
    def setup_buttons(self, main_layout):
        """Set up the action buttons section of the GUI"""
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        self.trim_btn = QPushButton("Trim Videos")
        self.trim_btn.clicked.connect(self.trim_videos)
        buttons_layout.addWidget(self.trim_btn)
        
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.exit_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def select_files(self):
        """Open file dialog to select video files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*.*)"
        )
        
        if files:
            self.selected_files = files
            self.file_list.clear()
            self.file_list.addItems([os.path.basename(f) for f in files])
            self.statusBar().showMessage(f"{len(files)} files selected")
    
    def clear_selection(self):
        """Clear the selected files list"""
        self.selected_files = []
        self.file_list.clear()
        self.statusBar().showMessage("Selection cleared")
    
    def toggle_end_time(self, state):
        """Enable/disable end time input based on checkbox state"""
        self.end_time.setEnabled(not bool(state))
    
    def trim_videos(self):
        """Process the selected videos with the specified trimming options"""
        if not self.selected_files:
            QMessageBox.warning(self, "No Files", "Please select at least one video file.")
            return
        
        start_time = self.start_time.value()
        
        # Determine end time based on checkbox
        if self.use_end_of_video.isChecked():
            end_time = None  # None means use the end of the video
        else:
            end_time = self.end_time.value()
            if end_time <= start_time:
                QMessageBox.warning(self, "Invalid Time", "End time must be greater than start time.")
                return
        
        # Create output folder
        if self.selected_files:
            base_dir = os.path.dirname(self.selected_files[0])
            output_dir = os.path.join(base_dir, "trimmed_videos")
            os.makedirs(output_dir, exist_ok=True)
        else:
            return
        
        # Set up progress tracking
        total_files = len(self.selected_files)
        self.progress_bar.setRange(0, total_files)
        self.progress_bar.setValue(0)
        
        # Process each file
        for i, file_path in enumerate(self.selected_files):
            try:
                self.status_label.setText(f"Processing: {os.path.basename(file_path)}")
                QApplication.processEvents()
                
                # Process the video
                output_file = os.path.join(output_dir, f"trimmed_{os.path.basename(file_path)}")
                self.video_processor.trim_video(file_path, output_file, start_time, end_time)
                
                # Update progress
                self.progress_bar.setValue(i + 1)
                percent = int(((i + 1) / total_files) * 100)
                self.status_label.setText(f"Processed: {os.path.basename(file_path)}")
                self.statusBar().showMessage(f"Progress: {percent}%")
                QApplication.processEvents()
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error processing {os.path.basename(file_path)}: {str(e)}")
        
        # All done
        self.status_label.setText("Completed")
        self.statusBar().showMessage(f"All videos processed and saved to '{output_dir}'")
        
        # Show completion message
        QMessageBox.information(
            self, 
            "Processing Complete", 
            f"All videos have been trimmed and saved to:\n{output_dir}"
        )


def main():
    """Main function to start the application"""
    app = QApplication(sys.argv)
    window = VideoTrimmerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()