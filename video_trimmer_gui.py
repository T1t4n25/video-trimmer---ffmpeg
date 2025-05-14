#!/usr/bin/env python3
"""
Video Trimmer GUI - A PyQt6 application for trimming video files
"""

import os
import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QListWidget, QCheckBox,
    QDoubleSpinBox, QMessageBox, QProgressBar, QFrame, QComboBox,
    QLineEdit, QTimeEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QTime, QTranslator, QLocale
from PyQt6.QtGui import QIcon, QFont

# Import video processor module
from video_processor import VideoProcessor



class TimeEdit(QWidget):
    """Custom time edit widget with HH:MM:SS.ms format"""
    
    timeChanged = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the time edit widget
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss.zzz")
        self.time_edit.setTimeRange(QTime(0, 0, 0), QTime(23, 59, 59, 999))
        self.time_edit.setTime(QTime(0, 0, 0))
        self.time_edit.timeChanged.connect(self._time_changed)
        
        self.layout.addWidget(self.time_edit)
    
    def _time_changed(self, qtime):
        """Convert QTime to seconds and emit signal"""
        hours = qtime.hour()
        minutes = qtime.minute()
        seconds = qtime.second()
        msecs = qtime.msec()
        
        total_seconds = hours * 3600 + minutes * 60 + seconds + msecs / 1000
        self.timeChanged.emit(total_seconds)
    
    def set_seconds(self, seconds):
        """Set the time from seconds value"""
        total_ms = int(seconds * 1000)
        hours = total_ms // 3600000
        total_ms %= 3600000
        minutes = total_ms // 60000
        total_ms %= 60000
        secs = total_ms // 1000
        ms = total_ms % 1000
        
        self.time_edit.setTime(QTime(hours, minutes, secs, ms))
    
    def seconds(self):
        """Get the current time in seconds"""
        qtime = self.time_edit.time()
        hours = qtime.hour()
        minutes = qtime.minute()
        seconds = qtime.second()
        msecs = qtime.msec()
        
        return hours * 3600 + minutes * 60 + seconds + msecs / 1000
    
    def update_layout_direction(self, direction):
        """Update the layout direction for this widget"""
        self.setLayoutDirection(direction)
        self.time_edit.setLayoutDirection(direction)


class VideoTrimmerGUI(QMainWindow):
    """Main window class for the Video Trimmer application"""
    
    def __init__(self):
        super().__init__()
        self.video_processor = VideoProcessor()
        self.selected_files = []
        self.setWindowTitle("Video Trimmer")
        self.resize(800, 600)
        
        # Set up translator
        self.translator = QTranslator()
        self.current_language = "en"  # Default language
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Language selection
        self.setup_language_selection(main_layout)
        
        # File selection section
        self.setup_file_selection(main_layout)
        
        # Trimming options section
        self.setup_trimming_options(main_layout)
        
        # Progress section
        self.setup_progress_section(main_layout)
        
        # Buttons section
        self.setup_buttons(main_layout)
        
        # Status bar
        self.statusBar().showMessage(self.tr("Ready"))
        
        # Apply initial translation
        self.update_language("en")
    
    def setup_language_selection(self, main_layout):
        """Set up the language selection dropdown"""
        lang_layout = QHBoxLayout()
        
        lang_label = QLabel(self.tr("Language:"))
        lang_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("العربية", "ar")  # Arabic
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.lang_combo)
        
        lang_layout.addStretch()
        
        main_layout.addLayout(lang_layout)
    def setup_font_for_language(self, language_code):
        """Set up proper font for the selected language"""
        if language_code == "ar":
            # List of fonts that work well with Arabic
            arabic_fonts = ["Tahoma", "Arial", "Segoe UI", "Traditional Arabic"]
            
            # Try to find an installed Arabic-compatible font
            selected_font = None
            for font_name in arabic_fonts:
                font = QFont(font_name)
                if font.exactMatch():
                    selected_font = font_name
                    break
            
            if selected_font:
                app = QApplication.instance()
                default_font = QFont(selected_font, 10)
                app.setFont(default_font)
        else:
            # Reset to default font for non-Arabic languages
            app = QApplication.instance()
            default_font = QFont("Arial", 10)
            app.setFont(default_font)

    def adjust_rtl_specific_widgets(self):
        """Make specific adjustments for RTL interfaces"""
        direction = Qt.LayoutDirection.RightToLeft if self.current_language == "ar" else Qt.LayoutDirection.LeftToRight
        
        # Update TimeEdit widgets
        self.start_time_edit.update_layout_direction(direction)
        self.end_time_edit.update_layout_direction(direction)
        
        if self.current_language == "ar":
            # For RTL languages, adjust alignment of certain widgets
            
            # Set text alignment for labels
            for label in self.findChildren(QLabel):
                label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            # Set text alignment for line edits
            for line_edit in self.findChildren(QLineEdit):
                line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            # Note: We removed the problematic QFileDialog line
        else:
            # For LTR languages, reset to default alignments
            for label in self.findChildren(QLabel):
                label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            for line_edit in self.findChildren(QLineEdit):
                line_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
                
    def setup_file_selection(self, main_layout):
        """Set up the file selection section of the GUI"""
        # File selection section
        file_section = QFrame()
        file_section.setFrameShape(QFrame.Shape.StyledPanel)
        file_layout = QVBoxLayout(file_section)
        
        # Header
        self.file_header = QLabel(self.tr("Video Files"))
        self.file_header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        file_layout.addWidget(self.file_header)
        
        # File selection buttons
        btn_layout = QHBoxLayout()
        
        self.select_btn = QPushButton(self.tr("Select Video Files"))
        self.select_btn.clicked.connect(self.select_files)
        btn_layout.addWidget(self.select_btn)
        
        self.clear_btn = QPushButton(self.tr("Clear Selection"))
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
        self.trim_header = QLabel(self.tr("Trimming Options"))
        self.trim_header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        trim_layout.addWidget(self.trim_header)
        
        # Start time
        start_layout = QHBoxLayout()
        self.start_label = QLabel(self.tr("Start Time:"))
        start_layout.addWidget(self.start_label)
        
        self.start_time_edit = TimeEdit()
        self.start_time_edit.set_seconds(0)
        start_layout.addWidget(self.start_time_edit)
        
        trim_layout.addLayout(start_layout)
        
        # End time
        end_layout = QHBoxLayout()
        self.end_label = QLabel(self.tr("End Time:"))
        end_layout.addWidget(self.end_label)
        
        self.end_time_edit = TimeEdit()
        self.end_time_edit.set_seconds(60)  # Default 1 minute
        end_layout.addWidget(self.end_time_edit)
        
        trim_layout.addLayout(end_layout)
        
        # Option to use end of video
        self.use_end_of_video = QCheckBox(self.tr("Use End of Video"))
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
        self.progress_label = QLabel(self.tr("Progress:"))
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        # Status message
        self.status_label = QLabel(self.tr("Ready"))
        progress_layout.addWidget(self.status_label)
        
        main_layout.addWidget(progress_section)
    
    def setup_buttons(self, main_layout):
        """Set up the action buttons section of the GUI"""
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        self.trim_btn = QPushButton(self.tr("Trim Videos"))
        self.trim_btn.clicked.connect(self.trim_videos)
        buttons_layout.addWidget(self.trim_btn)
        
        self.exit_btn = QPushButton(self.tr("Exit"))
        self.exit_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.exit_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def select_files(self):
        """Open file dialog to select video files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("Select Video Files"),
            "",
            self.tr("Video Files (*.mp4 *.avi *.mov *.mkv *.wmv);;All Files (*.*)")
        )
        
        if files:
            self.selected_files = files
            self.file_list.clear()
            self.file_list.addItems([os.path.basename(f) for f in files])
            self.statusBar().showMessage(self.tr("{} files selected").format(len(files)))
    
    def clear_selection(self):
        """Clear the selected files list"""
        self.selected_files = []
        self.file_list.clear()
        self.statusBar().showMessage(self.tr("Selection cleared"))
    
    def toggle_end_time(self, state):
        """Enable/disable end time input based on checkbox state"""
        self.end_time_edit.setEnabled(not bool(state))
    
    def trim_videos(self):
        """Process the selected videos with the specified trimming options"""
        if not self.selected_files:
            QMessageBox.warning(self, self.tr("No Files"), self.tr("Please select at least one video file."))
            return
        
        start_time = self.start_time_edit.seconds()
        
        # Determine end time based on checkbox
        if self.use_end_of_video.isChecked():
            end_time = None  # None means use the end of the video
        else:
            end_time = self.end_time_edit.seconds()
            if end_time <= start_time:
                QMessageBox.warning(self, self.tr("Invalid Time"), 
                                   self.tr("End time must be greater than start time."))
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
                self.status_label.setText(self.tr("Processing: {}").format(os.path.basename(file_path)))
                QApplication.processEvents()
                
                # Process the video
                output_file = os.path.join(output_dir, f"trimmed_{os.path.basename(file_path)}")
                self.video_processor.trim_video(file_path, output_file, start_time, end_time)
                
                # Update progress
                self.progress_bar.setValue(i + 1)
                percent = int(((i + 1) / total_files) * 100)
                self.status_label.setText(self.tr("Processed: {}").format(os.path.basename(file_path)))
                self.statusBar().showMessage(self.tr("Progress: {}%").format(percent))
                QApplication.processEvents()
                
            except Exception as e:
                QMessageBox.warning(self, self.tr("Error"), 
                                   self.tr("Error processing {}: {}").format(os.path.basename(file_path), str(e)))
        
        # All done
        self.status_label.setText(self.tr("Completed"))
        self.statusBar().showMessage(self.tr("All videos processed and saved to '{}'").format(output_dir))
        
        # Show completion message
        QMessageBox.information(
            self, 
            self.tr("Processing Complete"), 
            self.tr("All videos have been trimmed and saved to:\n{}").format(output_dir)
        )
    
    def on_language_changed(self, index):
        """Handle language change from dropdown"""
        language_code = self.lang_combo.itemData(index)
        self.update_language(language_code)
    
    def update_language(self, language_code):
        """Update the UI language"""
        self.current_language = language_code
        
        # Load translation file for the selected language
        if language_code != "en":  # English is the default language (no translation needed)
            # Find the translation file in the translations folder
            translations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations")
            translation_file = os.path.join(translations_dir, f"video_trimmer_{language_code}.qm")
            
            # Load the translation
            if os.path.exists(translation_file):
                self.translator.load(translation_file)
                QApplication.instance().installTranslator(self.translator)
            else:
                print(f"Translation file not found: {translation_file}")
                return
        else:
            # Remove translator for English
            QApplication.instance().removeTranslator(self.translator)
        
        # Set layout direction based on language
        if language_code == "ar":
            # Set Right-to-Left layout direction for Arabic
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            QApplication.instance().setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            # Set Left-to-Right layout direction for other languages
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            QApplication.instance().setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
        # Set up appropriate font
        self.setup_font_for_language(language_code)
        
        # Update UI text
        self.retranslateUi()
        
        # Adjust specific widgets for RTL/LTR
        self.adjust_rtl_specific_widgets()
    
    def retranslateUi(self):
        """Update all UI text with current language"""
        # Window title
        self.setWindowTitle(self.tr("Video Trimmer"))
        
        # File section
        self.file_header.setText(self.tr("Video Files"))
        self.select_btn.setText(self.tr("Select Video Files"))
        self.clear_btn.setText(self.tr("Clear Selection"))
        
        # Trimming options
        self.trim_header.setText(self.tr("Trimming Options"))
        self.start_label.setText(self.tr("Start Time:"))
        self.end_label.setText(self.tr("End Time:"))
        self.use_end_of_video.setText(self.tr("Use End of Video"))
        
        # Progress section
        self.progress_label.setText(self.tr("Progress:"))
        if not self.status_label.text() or self.status_label.text() == "Ready":
            self.status_label.setText(self.tr("Ready"))
        
        # Buttons
        self.trim_btn.setText(self.tr("Trim Videos"))
        self.exit_btn.setText(self.tr("Exit"))
        
        # Status bar
        if self.statusBar().currentMessage() == "Ready":
            self.statusBar().showMessage(self.tr("Ready"))


def main():
    """Main function to start the application"""
    app = QApplication(sys.argv)
    window = VideoTrimmerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()