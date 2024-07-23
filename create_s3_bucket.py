import boto3
import json

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

if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)
    create_s3_bucket(config)
