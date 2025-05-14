# Video Trimmer Application

A PyQt6-based application for trimming video files. This application allows users to select one or more video files, specify start and end times, and trim the videos accordingly.

## Features

- Select multiple video files for batch processing
- Set start and end times for trimming
- Option to use the end of the video as the trim endpoint
- Video processing with ffmpeg (using the ffmpeg-python wrapper)
- Progress tracking for batch operations
- Dedicated output folder for trimmed videos

## Requirements

- Python 3.6+
- PyQt6
- ffmpeg (system installation)
- ffmpeg-python

## Installation

1. Ensure you have Python 3.6 or later installed
2. Install ffmpeg on your system:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` or equivalent for your distro
3. Install the required Python packages:

```bash
pip install PyQt6 ffmpeg-python
```

## Usage

Run the application by executing the main script:

```bash
python main.py
```

### Steps to Trim Videos:

1. Click "Select Video Files" to choose one or more video files.
2. Set the start time in seconds.
3. Either:
   - Set the end time in seconds, or
   - Check "Use End of Video" to use the full duration.
4. Click "Trim Videos" to process all selected files.
5. Trimmed videos will be saved in a "trimmed_videos" folder in the same directory as the input files.

## Project Structure

- `main.py` - Application entry point
- `video_trimmer_gui.py` - GUI implementation using PyQt6
- `video_processor.py` - Video processing logic using ffmpeg

## Development

To modify the application:

1. Clone the repository
2. Make your changes
3. Test by running `main.py`

## Contributing

Contributions are welcome! Feel free to submit pull requests or report issues.

## License

This project is licensed under the MIT License.