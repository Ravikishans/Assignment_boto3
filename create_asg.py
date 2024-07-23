import boto3
import json

def create_launch_configuration(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.create_launch_configuration(
        LaunchConfigurationName='my-launch-configuration',
        ImageId='ami-056a29f2eddc40520',
        InstanceType='t3.micro',
        KeyName=config['key_pair_name'],
        SecurityGroups=[config['security_group_id']],
        UserData='''#!/bin/bash
                    sudo apt update -y
                    sudo apt install nginx -y
                    sudo service nginx start
                    sudo service nginx enable
                    echo "Hello, World!" > /var/www/html/index.html
                    sudo service nginx reload'''
    )
    print("Launch configuration created successfully.")

def create_auto_scaling_group(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='my-auto-scaling-group',
        LaunchConfigurationName='my-launch-configuration',
        MinSize=1,
        MaxSize=3,
        DesiredCapacity=1,
        VPCZoneIdentifier=f"{config['subnet1_id']},{config['subnet2_id']}",
        TargetGroupARNs=[config['target_group_arn']]
    )
    print("Auto Scaling Group created successfully.")

def configure_scaling_policy(config):
    autoscaling = boto3.client('autoscaling', region_name=config['region'])

    autoscaling.put_scaling_policy(
        AutoScalingGroupName='my-auto-scaling-group',
        PolicyName='scale-out',
        PolicyType='TargetTrackingScaling',
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'ASGAverageCPUUtilization'
            },
            'TargetValue': 50.0
        }
    )
    print("Scaling policy configured successfully.")

if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)

    create_launch_configuration(config)
    create_auto_scaling_group(config)
    configure_scaling_policy(config)
