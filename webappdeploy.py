import boto3
from botocore.exceptions import ClientError
import logging
import os

#creating a S3 bucket

# s3= boto3.resource("s3")
# for bucket in s3.buckets.all():
#     print(bucket.name)

def create_bucket(bucket_name, region=None):
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_file(file_name, bucket, object_name=None):

    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__=="__main__":
    create_bucket(bucket_name="rakshi2107", region= "ap-northeast-2")
    upload_file(file_name=r"C:\Users\Ravik\Pictures\Screenshots\containarize.png",bucket="rakshi2107",object_name=None)