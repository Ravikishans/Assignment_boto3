import boto3
from botocore.exceptions import ClientError
import logging
import os
import create_vpc

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

def create_ec2_instance():
    
    ec2= boto3.client("ec2")
    instance_params = {
        'ImageId': 'ami-056a29f2eddc40520',  # Replace with a valid image ID
        'InstanceType': 't3.micro',
        'MinCount': 2,
        'MaxCount': 2,
        'KeyName': 'raviAWS',  # Replace with your key pair name
        # 'SecurityGroupIds': ['Default'],  # Replace with your security group ID
        'SubnetId': subnet1_id,  # Replace with your subnet ID
        'TagSpecifications': [{
            'ResourceType': 'instance',
            'Tags': [{
                'Key': 'Name',
                'Value': 'RaviScaling'
            }]
        }],
        'UserData': '''#!/bin/bash
            sudo apt update -y
            sudo apt install nginx -y
            sudo service nginx start
            sudo service nginx enable
        '''
    }
    instance = ec2.run_instances(**instance_params)
    
    instance_id = instance['Instances'][0]['InstanceId']
    print(f'EC2 instance created with ID: {instance_id}')
    
    return instance_id


if __name__=="__main__":
    vpc_id, subnet1_id, subnet2_id, igw_id, route_table_id = create_vpc.create_vpc()
    create_bucket(bucket_name="rakshi2107", region= "ap-northeast-2")
    upload_file(file_name=r"C:\Users\Ravik\Pictures\Screenshots\containarize.png",bucket="rakshi2107",object_name=None)
    create_ec2_instance()
