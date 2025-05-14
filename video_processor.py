#!/usr/bin/env python3
"""
Video processor module for the Video Trimmer application
Handles all video processing operations
"""

import os
import subprocess
from typing import Optional
import ffmpeg


class VideoProcessor:
    """Class for processing video files using ffmpeg"""
    
    def __init__(self):
        """Initialize the video processor"""
        # Set up ffmpeg path
        self.ffmpeg_path = self._get_ffmpeg_path()
        # Verify ffmpeg is accessible
        self._check_ffmpeg()
    
    def _get_ffmpeg_path(self) -> str:
        """
        Determine the path to ffmpeg executable
        First checks for bundled ffmpeg, then falls back to system ffmpeg
        
        Returns:
            Path to ffmpeg executable
        """
        import sys
        import platform
        
        # Get the directory where the script or executable is located
        if getattr(sys, 'frozen', False):
            # We're running in a bundle (PyInstaller or similar)
            base_path = sys._MEIPASS
        else:
            # We're running in a normal Python environment
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Check platform to determine executable name and location
        system = platform.system()
        
        if system == "Windows":
            # For Windows, check the 'ffmpeg' subdirectory
            ffmpeg_dir = os.path.join(base_path, 'ffmpeg', 'bin')
            ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
            
            if os.path.isfile(ffmpeg_exe):
                return ffmpeg_dir  # Return directory containing ffmpeg
            
        elif system == "Darwin":  # macOS
            # For macOS, check the 'ffmpeg' subdirectory
            ffmpeg_dir = os.path.join(base_path, 'ffmpeg')
            ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg')
            
            if os.path.isfile(ffmpeg_exe):
                return ffmpeg_dir
                
        elif system == "Linux":
            # For Linux, check the 'ffmpeg' subdirectory
            ffmpeg_dir = os.path.join(base_path, 'ffmpeg')
            ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg')
            
            if os.path.isfile(ffmpeg_exe):
                return ffmpeg_dir
        
        # If no bundled ffmpeg is found, return None to use system ffmpeg
        return None
    
    def _check_ffmpeg(self) -> None:
        """Check if ffmpeg is installed and accessible"""
        try:
            # If we have a bundled ffmpeg path, use it for the check
            if self.ffmpeg_path:
                # Set environment variable for ffmpeg-python to use our bundled ffmpeg
                os.environ["FFMPEG_BINARY"] = os.path.join(self.ffmpeg_path, "ffmpeg")
                os.environ["FFPROBE_BINARY"] = os.path.join(self.ffmpeg_path, "ffprobe")
                
                # Test the bundled ffmpeg
                subprocess.run(
                    [os.path.join(self.ffmpeg_path, "ffmpeg"), "-version"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    check=True
                )
            else:
                # Fall back to system ffmpeg
                subprocess.run(
                    ["ffmpeg", "-version"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    check=True
                )
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError(
                "FFmpeg not found. Either bundle ffmpeg with the application or "
                "install FFmpeg on your system. Visit https://ffmpeg.org/download.html for instructions."
            )
    
    def get_video_duration(self, file_path: str) -> float:
        """
        Get the duration of a video file in seconds
        
        Args:
            file_path: Path to the video file
            
        Returns:
            Duration of the video in seconds
        """
        try:
            probe = ffmpeg.probe(file_path)
            video_info = next(
                stream for stream in probe['streams'] 
                if stream['codec_type'] == 'video'
            )
            return float(probe['format']['duration'])
        except ffmpeg.Error as e:
            raise ValueError(f"Error probing video file: {e.stderr.decode()}")
        except (KeyError, StopIteration):
            raise ValueError("Could not determine video duration")
    
    def trim_video(
        self, 
        input_file: str, 
        output_file: str, 
        start_time: float, 
        end_time: Optional[float] = None
    ) -> str:
        """
        Trim a video file and save the result
        
        Args:
            input_file: Path to the input video file
            output_file: Path to save the trimmed video
            start_time: Start time in seconds
            end_time: End time in seconds, or None to use the end of the video
            
        Returns:
            Path to the output file
        """
        # Validate input file
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Get video duration if end_time is None
        if end_time is None:
            end_time = self.get_video_duration(input_file)
        
        # Validate times
        if start_time < 0:
            raise ValueError("Start time cannot be negative")
        
        if end_time <= start_time:
            raise ValueError("End time must be greater than start time")
        
        # Create the FFmpeg input
        input_stream = ffmpeg.input(input_file, ss=start_time, to=end_time)
        
        # Set up the output with the same codec to avoid re-encoding (fast copy)
        output_stream = ffmpeg.output(
            input_stream, 
            output_file,
            c='copy',  # Use copy mode for faster processing
            avoid_negative_ts='make_zero'  # Adjust timestamps
        )
        
        try:
            # Run the FFmpeg command
            ffmpeg.run(
                output_stream, 
                capture_stdout=True, 
                capture_stderr=True, 
                overwrite_output=True
            )
            return output_file
        except ffmpeg.Error as e:
            # If copy mode fails (some formats don't support it), try re-encoding
            try:
                input_stream = ffmpeg.input(input_file, ss=start_time, to=end_time)
                output_stream = ffmpeg.output(input_stream, output_file)
                ffmpeg.run(
                    output_stream, 
                    capture_stdout=True, 
                    capture_stderr=True, 
                    overwrite_output=True
                )
                return output_file
            except ffmpeg.Error as e2:
                error_message = e2.stderr.decode() if hasattr(e2, 'stderr') else str(e2)
                raise RuntimeError(f"Error trimming video: {error_message}")
    
    def get_video_info(self, file_path: str) -> dict:
        """
        Get detailed information about a video file
        
        Args:
            file_path: Path to the video file
            
        Returns:
            Dictionary with video information
        """
        try:
            probe = ffmpeg.probe(file_path)
            
            # Extract basic format info
            format_info = probe['format']
            
            # Extract video stream info
            video_stream = next(
                (stream for stream in probe['streams'] 
                if stream['codec_type'] == 'video'),
                None
            )
            
            # Extract audio stream info
            audio_stream = next(
                (stream for stream in probe['streams'] 
                if stream['codec_type'] == 'audio'),
                None
            )
            
            # Compile the info
            info = {
                'filename': os.path.basename(file_path),
                'format': format_info.get('format_name', 'Unknown'),
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bitrate': int(format_info.get('bit_rate', 0)),
            }
            
            # Add video stream info if available
            if video_stream:
                info['video'] = {
                    'codec': video_stream.get('codec_name', 'Unknown'),
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'fps': self._parse_fps(video_stream),
                }
            
            # Add audio stream info if available
            if audio_stream:
                info['audio'] = {
                    'codec': audio_stream.get('codec_name', 'Unknown'),
                    'channels': int(audio_stream.get('channels', 0)),
                    'sample_rate': int(audio_stream.get('sample_rate', 0)),
                }
            
            return info
        
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if hasattr(e, 'stderr') else str(e)
            raise ValueError(f"Error getting video info: {error_message}")
    
    def _parse_fps(self, video_stream: dict) -> float:
        """
        Parse the frame rate from a video stream
        
        Args:
            video_stream: Video stream dictionary from ffmpeg probe
            
        Returns:
            Frame rate as a float
        """
        # Try to get the frame rate
        if 'avg_frame_rate' in video_stream:
            try:
                num, den = map(int, video_stream['avg_frame_rate'].split('/'))
                if den != 0:
                    return num / den
            except (ValueError, ZeroDivisionError):
                pass
        
        # If the above fails, try the 'r_frame_rate'
        if 'r_frame_rate' in video_stream:
            try:
                num, den = map(int, video_stream['r_frame_rate'].split('/'))
                if den != 0:
                    return num / den
            except (ValueError, ZeroDivisionError):
                pass
        
        # Default to 0 if we can't determine the frame rate
        return 0.0


if __name__ == "__main__":
    # This block allows for simple testing of the module
    processor = VideoProcessor()
    print("FFmpeg is installed and ready for use.")
    
    # Example usage:
    # processor.trim_video('input.mp4', 'output.mp4', 10, 20)