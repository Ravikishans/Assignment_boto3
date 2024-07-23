import create_s3_bucket
import create_vpc
import launch_ec2_instance
import deploy_alb
import create_asg
import setup_sns_notifications
import sys
import json
import boto3

def deploy_infrastructure():
    with open('config.json') as f:
        config = json.load(f)

    # Step 1: Create S3 Bucket
    create_s3_bucket.create_s3_bucket(config)
    
    # Step 2: Create VPC
    create_vpc.create_vpc()
    
    with open('config.json') as f:
        config = json.load(f)

    # Step 3: Launch EC2 Instances
    instance_id1 = launch_ec2_instance.launch_ec2_instance(config, config['subnet1_id'])
    instance_id2 = launch_ec2_instance.launch_ec2_instance(config, config['subnet2_id'])
    
    config.update({
        "instance_ids": [instance_id1, instance_id2]
    })
    
    with open('config.json', 'w') as f:
        json.dump(config, f)

    # Step 4: Deploy Application Load Balancer
    load_balancer_arn = deploy_alb.deploy_alb(config)
    target_group_arn = deploy_alb.create_target_group(config)
    deploy_alb.register_targets(config, target_group_arn)
    deploy_alb.create_listener(load_balancer_arn, target_group_arn, config)
    
    config.update({
        "load_balancer_arn": load_balancer_arn,
        "target_group_arn": target_group_arn
    })

    with open('config.json', 'w') as f:
        json.dump(config, f)

    # Step 5: Create Auto Scaling Group
    create_asg.create_launch_configuration(config)
    create_asg.create_auto_scaling_group(config)
    create_asg.configure_scaling_policy(config)

    # Step 6: Set Up SNS Topics for Notifications
    setup_sns_notifications.create_sns_topics(config)

    with open('config.json') as f:
        config = json.load(f)

    setup_sns_notifications.subscribe_to_sns_topic(config['health_topic_arn'], 'email', config['admin_email'])
    # setup_sns_notifications.subscribe_to_sns_topic(config['scaling_topic_arn'], 'sms', config['admin_phone'])

    print("Infrastructure deployment completed successfully.")


def update_infrastructure():
    with open('config.json') as f:
        config = json.load(f)
    
    ec2 = boto3.client('ec2', region_name=config['region'])
    elbv2 = boto3.client('elbv2', region_name=config['region'])
    asg = boto3.client('autoscaling', region_name=config['region'])
    sns = boto3.client('sns', region_name=config['region'])
    
    # Update EC2 Instances
    print("Updating EC2 instances...")
    ec2.instances.filter(InstanceIds=config['instance_ids']).modify_attribute(
        InstanceType={'Value': 't2.medium'}  # Example of changing instance type
    )
    print("EC2 instances updated successfully.")
    
    # Update Load Balancer
    print("Updating Load Balancer...")
    elbv2.modify_load_balancer_attributes(
        LoadBalancerArn=config['load_balancer_arn'],
        Attributes=[{
            'Key': 'idle_timeout.timeout_seconds',
            'Value': '60'  # Example of updating attribute
        }]
    )
    print("Load Balancer updated successfully.")
    
    # Update Auto Scaling Group
    print("Updating Auto Scaling Group...")
    asg.update_auto_scaling_group(
        AutoScalingGroupName='my-auto-scaling-group',
        MinSize=2,  # Example of increasing min size
        MaxSize=5,  # Example of increasing max size
        DesiredCapacity=2  # Example of setting desired capacity
    )
    print("Auto Scaling Group updated successfully.")
    
    # Update SNS Topics
    print("Updating SNS topics...")
    sns.subscribe(TopicArn=config['health_topic_arn'], Protocol='email', Endpoint='new_admin@example.com')
    # sns.subscribe(TopicArn=config['scaling_topic_arn'], Protocol='sms', Endpoint='+0987654321')
    print("SNS topics updated successfully.")
    
    print("Infrastructure update completed successfully.")


def tear_down_infrastructure():
    with open('config.json') as f:
        config = json.load(f)
    
    ec2 = boto3.resource('ec2', region_name=config['region'])
    elbv2 = boto3.client('elbv2', region_name=config['region'])
    asg = boto3.client('autoscaling', region_name=config['region'])
    sns = boto3.client('sns', region_name=config['region'])
    
    # Terminate EC2 instances
    for instance_id in config['instance_ids']:
        instance = ec2.Instance(instance_id)
        instance.terminate()
        instance.wait_until_terminated()
        print(f"EC2 instance '{instance_id}' terminated successfully.")
    
    # Delete load balancer
    elbv2.delete_load_balancer(LoadBalancerArn=config['load_balancer_arn'])
    print(f"Load balancer '{config['load_balancer_arn']}' deleted successfully.")
    
    
    
    # Delete Auto Scaling group
    asg.delete_auto_scaling_group(
        AutoScalingGroupName='my-auto-scaling-group',
        ForceDelete=True
    )
    print("Auto Scaling Group deleted successfully.")
    
    # Delete target group
    elbv2.delete_target_group(TargetGroupArn=config['target_group_arn'])
    print(f"Target group '{config['target_group_arn']}' deleted successfully.")

    # Delete launch configuration
    asg.delete_launch_configuration(
        LaunchConfigurationName='my-launch-configuration'
    )
    print("Launch configuration deleted successfully.")    


    # Delete SNS topics
    sns.delete_topic(TopicArn=config['health_topic_arn'])
    sns.delete_topic(TopicArn=config['scaling_topic_arn'])
    print("SNS topics deleted successfully.")
    
    # # Detach and delete Internet Gateway
    # ec2.detach_internet_gateway(InternetGatewayId=config['igw_id'], VpcId=config['vpc_id'])
    # ec2.delete_internet_gateway(InternetGatewayId=config['igw_id'])
    # print(f"Internet Gateway '{config['igw_id']}' deleted successfully.")

    # Delete security group
    ec2.SecurityGroup(config['security_group_id']).delete()
    print(f"Security Group '{config['security_group_id']}' deleted successfully.")
    
    # # Delete subnets
    # ec2.Subnet(config['subnet1_id']).delete()
    # ec2.Subnet(config['subnet2_id']).delete()
    # print(f"Subnets '{config['subnet1_id']}' and '{config['subnet2_id']}' deleted successfully.")
    
    # # Delete route table
    # ec2.RouteTable(config['route_table_id']).delete()
    # print(f"Route Table '{config['route_table_id']}' deleted successfully.")
    
    # Delete VPC
    ec2.Vpc(config['vpc_id']).delete()
    print(f"VPC '{config['vpc_id']}' deleted successfully.")
    
    # Delete S3 bucket
    s3 = boto3.client('s3', region_name=config['region'])
    s3.delete_bucket(Bucket=config['bucket_name'])
    print(f"S3 bucket '{config['bucket_name']}' deleted successfully.")
    
    print("Infrastructure tear down completed successfully.")



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_infrastructure.py <deploy|update|teardown>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "deploy":
        deploy_infrastructure()
    elif command == "update":
        update_infrastructure()
    elif command == "teardown":
        tear_down_infrastructure()
    else:
        print("Invalid command. Use 'deploy', 'update', or 'teardown'.")
        sys.exit(1)
