import streamlit as st
import boto3
import requests
import tempfile
import os
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


s3_client = boto3.client('s3', region_name=os.getenv("AWS_REGION"))
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=os.getenv("AWS_REGION"))

def download_video_from_url(url):
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    chunks = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            chunks.append(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                progress = downloaded / total_size
                progress_bar.progress(progress)
                status_text.text(f"Downloaded: {downloaded/1024/1024:.1f} MB / {total_size/1024/1024:.1f} MB")
    
    progress_bar.empty()
    status_text.empty()
    return b''.join(chunks)

def upload_to_s3(file_bytes, filename, bucket):
    key = f"{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4().hex[:8]}_{filename}"
    s3_client.put_object(Bucket=bucket, Key=key, Body=file_bytes)
    return key

def check_s3_output(output_key, max_wait=600, interval=10):
    waited = 0
    while waited < max_wait:
        try:
            s3_client.head_object(Bucket=os.getenv("S3_OUTPUT_BUCKET"), Key=output_key)
            return True
        except:
            time.sleep(interval)
            waited += interval
    return False

def download_from_s3(key, bucket):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()

def trigger_sagemaker_async(input_s3_path, output_s3_path, gender):
    payload = {
        "input_video": input_s3_path,
        "output_video": output_s3_path,
        "gender": gender
    }
    
    response = sagemaker_runtime.invoke_endpoint_async(
        EndpointName=os.getenv("SAGEMAKER_ENDPOINT"),
        InputLocation=f"s3://{os.getenv('S3_INPUT_BUCKET')}/{input_s3_path}",
        InferenceId=str(uuid.uuid4())
    )
    return response

def main():
    st.set_page_config(page_title="Voice Conversion", layout="centered")
    st.title("Voice Conversion Dashboard")
    
    input_method = st.radio("Select Input Method", ["Upload Video File", "Video URL"])
    
    video_bytes = None
    filename = None
    
    if input_method == "Upload Video File":
        uploaded_file = st.file_uploader("Upload Video", type=['mp4', 'mov', 'avi', 'mkv'])
        if uploaded_file:
            video_bytes = uploaded_file.read()
            filename = uploaded_file.name
    else:
        video_url = st.text_input("Enter Video URL (Vimeo, YouTube, Direct Link)")
        if video_url:
            filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
    
    voice_gender = st.selectbox("Voice Gender", ["Male", "Female"])
    
    if st.button("Process Video"):
        if input_method == "Upload Video File" and not video_bytes:
            st.error("Upload a video file")
            return
        
        if input_method == "Video URL" and not video_url:
            st.error("Enter a valid video URL")
            return
        
        try:
            if input_method == "Video URL":
                with st.spinner("Downloading video from URL..."):
                    video_bytes = download_video_from_url(video_url)
                    st.success(f"Downloaded {len(video_bytes)/1024/1024:.1f} MB")
            
            with st.spinner("Uploading to S3..."):
                input_key = upload_to_s3(video_bytes, filename, os.getenv("S3_INPUT_BUCKET"))
                st.success(f"Uploaded: {input_key}")
            
            output_key = input_key.rsplit('.', 1)[0] + "_converted.mp4"
            
            with st.spinner("Triggering SageMaker processing..."):
                trigger_sagemaker_async(input_key, output_key, voice_gender)
                st.info("Job submitted. Processing may take 3-10 minutes.")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(60):
                if check_s3_output(output_key, max_wait=10, interval=1):
                    progress_bar.progress(100)
                    status_text.success("Processing complete!")
                    break
                progress_bar.progress(min((i + 1) * 2, 95))
                status_text.text(f"Processing... {i+1}/60 checks")
                time.sleep(10)
            else:
                st.warning("Processing taking longer than expected. Check back later.")
                st.info(f"Output key: {output_key}")
                return
            
            with st.spinner("Downloading processed video..."):
                output_video = download_from_s3(output_key, os.getenv("S3_OUTPUT_BUCKET"))
            
            st.download_button(
                "Download Converted Video",
                output_video,
                f"converted_{filename}",
                "video/mp4"
            )
            
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to download video from URL: {str(e)}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()