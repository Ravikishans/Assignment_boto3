import boto3
import json

def launch_ec2_instance(config, subnet_id):
    ec2 = boto3.resource('ec2', region_name=config['region'])

    instances = ec2.create_instances(
        ImageId='ami-056a29f2eddc40520',
        MinCount=1,
        MaxCount=1,
        InstanceType='t3.micro',
        KeyName=config['key_pair_name'],
        SecurityGroupIds=[config['security_group_id']],
        SubnetId=subnet_id,
        UserData='''#!/bin/bash
                    sudo apt update -y
                    sudo apt install nginx -y
                    sudo service nginx start
                    sudo service nginx enable
                    echo "Hello, World!" > /var/www/html/index.html
                    sudo service nginx reload''',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': "raviScaling"
                    }
                ]
            }
        ]
    )
    instance_id = instances[0].id
    print(f"EC2 instance '{instance_id}' launched successfully.")
    return instance_id

if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)

    instance_id1 = launch_ec2_instance(config, config['subnet1_id'])
    instance_id2 = launch_ec2_instance(config, config['subnet2_id'])
    
    config.update({
        "instance_ids": [instance_id1, instance_id2]
    })

    with open('config.json', 'w') as f:
        json.dump(config, f)
