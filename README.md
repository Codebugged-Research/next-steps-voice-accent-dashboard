# Voice Conversion Dashboard

## Overview
The Voice Conversion Dashboard is a Streamlit-based web application designed to process and convert the voice in video files. It leverages AWS services such as S3 and SageMaker to handle video uploads, processing, and downloads. The application supports both file uploads and video URLs as input sources.

## Features
- **Input Methods**: Users can upload video files or provide video URLs (e.g., Vimeo, YouTube, or direct links).
- **Voice Gender Selection**: Choose between male and female voice conversion.
- **AWS Integration**: Utilizes S3 for storage and SageMaker for processing.
- **Progress Tracking**: Displays progress for video download, upload, and processing.
- **Download Processed Video**: Allows users to download the converted video directly from the dashboard.

## Prerequisites
1. **AWS Credentials**: Ensure you have AWS credentials configured with access to the required S3 buckets and SageMaker endpoint.
2. **Environment Variables**: Create a `.env` file in the project directory with the following variables:
   ```
   AWS_REGION=<your-aws-region>
   S3_INPUT_BUCKET=<your-input-bucket-name>
   S3_OUTPUT_BUCKET=<your-output-bucket-name>
   SAGEMAKER_ENDPOINT=<your-sagemaker-endpoint-name>
   ```
3. **Python Dependencies**: Install the required Python packages using the `requirements.txt` file.

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rvc-model-dashboard
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run dashboard.py
   ```

## Usage
1. Open the application in your browser (default: `http://localhost:8501`).
2. Select an input method (upload video file or provide a video URL).
3. Choose the desired voice gender for conversion.
4. Click the "Process Video" button to start the conversion process.
5. Download the processed video once the conversion is complete.

## AWS Services Used
- **Amazon S3**: For storing input and output video files.
- **Amazon SageMaker**: For processing and converting the voice in videos.

## Error Handling
- Handles video download errors (e.g., invalid URLs, network issues).
- Displays appropriate error messages for missing inputs or processing failures.

## License
This project is licensed under the MIT License. See the LICENSE file for details.