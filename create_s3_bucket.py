import boto3
import json
from botocore.exceptions import ClientError
import logging
import os

def create_s3_bucket(config):
    s3 = boto3.client('s3', region_name=config['region'])
    location = {'LocationConstraint': config['region']}

    try:
        if config['region'] == 'us-east-1':
            s3.create_bucket(Bucket=config['bucket_name'])
        else:
            s3.create_bucket(
                Bucket=config['bucket_name'],
                CreateBucketConfiguration=location
            )
        print(f"S3 bucket '{config['bucket_name']}' created successfully in region '{config['region']}'.")
    except Exception as e:
        print(f"Error creating S3 bucket: {e}")

def upload_file(file_name, bucket, object_name=None):

    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True

if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)
    create_s3_bucket(config)
    upload_file(file_name=r"C:\Users\Ravik\Pictures\Screenshots\containarize.png",bucket="rakshi2508",object_name=None)