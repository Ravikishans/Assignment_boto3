import boto3
import json
import time

def launch_ec2_instance(config, subnet_id):
    ec2 = boto3.resource('ec2', region_name=config['region'])

    instances = ec2.create_instances(
        ImageId='ami-056a29f2eddc40520',
        MinCount=1,
        MaxCount=1,
        InstanceType='t3.micro',
        KeyName=config['key_pair_name'],
        # SecurityGroupIds=[config['security_group_id']],
        # SubnetId=subnet_id,
        # AssociatePublicIpAddress=True,
        UserData='''#!/bin/bash
        sudo apt-get update -y
        sudo apt-get install nginx -y
        sudo apt-get install python3-pip -y
        sudo pip3 install flask boto3
        mkdir /home/ubuntu/app
        echo "
        from flask import Flask, request, redirect, url_for
        import os

        app = Flask(__name__)
        UPLOAD_FOLDER = '/home/ubuntu/uploads'
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        @app.route('/')
        def index():
            return \'''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <title>Upload new File</title>
          </head>
          <body>
            <h1>Upload new File</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
              <input type="file" name="file">
              <input type="submit" value="Upload">
            </form>
          </body>
        </html>\'''

        @app.route('/upload', methods=['POST'])
        def upload_file():
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('index'))
            return 'File not allowed.'

        if __name__ == '__main__':
            app.run(host='0.0.0.0', port=80)
        " > /home/ubuntu/app/app.py

        sudo mkdir /home/ubuntu/uploads
        sudo chmod -R 777 /home/ubuntu/uploads
        nohup python3 /home/ubuntu/app/app.py > /home/ubuntu/app/app.log 2>&1 &
        ''',
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
        ],
        NetworkInterfaces=[
            {
                'SubnetId': subnet_id,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': True,
                'Groups': [config['security_group_id']]
            }
        ]
    )
    
    instance_id = instances[0].id
    print(f"EC2 instance '{instance_id}' launched successfully.")

    # Wait until the instance is running
    ec2.meta.client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f"EC2 instance '{instance_id}' is now running.")

    instance = instances[0]
    instance.reload()
    public_ip = instance.public_ip_address
    print(f"Public IP of instance '{instance_id}': {public_ip}")

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
