import boto3
import os
from dotenv import load_dotenv

# Load AWS credentials from .env
ENV_DIR = os.path.join(os.path.dirname(__file__), "environment")
if not os.path.exists(ENV_DIR):
    os.makedirs(ENV_DIR, exist_ok=True) 

ENV_FILE_PATH = os.path.join(os.path.dirname(__file__), ".env")
if not os.path.exists(ENV_FILE_PATH):
    with open(ENV_FILE_PATH, "w") as f:
        f.write("[default]\n")

load_dotenv(ENV_FILE_PATH)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def upload_file_to_s3(file_path, bucket_name):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    chunk_size = 50 * 1024 * 1024  # 50 MB
    total_parts = (file_size // chunk_size) + (1 if file_size % chunk_size != 0 else 0)

    # Start multipart upload
    response = s3.create_multipart_upload(Bucket=bucket_name, Key=file_name)
    upload_id = response["UploadId"]

    print(f"Starting upload: {file_name} to {bucket_name}")
    parts = []
    try:
        with open(file_path, "rb") as f:
            for part_number in range(1, total_parts + 1):
                chunk = f.read(chunk_size)
                response = s3.upload_part(
                    Bucket=bucket_name,
                    Key=file_name,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=chunk,
                )
                parts.append({"ETag": response["ETag"], "PartNumber": part_number})
                print(f"Uploaded part {part_number}/{total_parts}")

        # Complete the upload
        s3.complete_multipart_upload(
            Bucket=bucket_name,
            Key=file_name,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},
        )
        print(f"Upload complete: {file_name}")

    except Exception as e:
        # Abort multipart upload on error
        s3.abort_multipart_upload(Bucket=bucket_name, Key=file_name, UploadId=upload_id)
        print(f"Upload failed: {e}")
        raise
