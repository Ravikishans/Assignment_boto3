import boto3
from botocore.exceptions import ClientError
import logging
import os

def deploy_alb():
    elbv2 = boto3.client('elbv2')
    load_balancer = elbv2.create_loadbalancer(
        Name= "RaviLB",
        Scheme='internet-facing',
        Type = 'application',
        IpAddressTyoe= 'ipv4'
    )
    load_balancer_arn = load_balancer['LoadBalancers'][0]['LoadBalancerArn']
    print(f"ALB '{load_balancer_arn}' created successfully.")
    return load_balancer_arn

def create_target_group(vpc_id):
    elbv2 = boto3.client('elbv2')
    target_group = elbv2.create_target_group(
        Name= 'ravi-target-group',
        Protocol='HTTP',
        Port=80,
        VpcId=vpc_id,
        HealthCheckProtocol='HTTP'
        HealthCheckPort='80',
        HealthcheckPath='/',
        TargetType='instance'
    )
    target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']
    print(f"Target group '{target_group_arn}' created successfully.")

    return target_group_arn

def register_targets(target_group_arn,instance_ids):
    elbv2 = boto3.client('elbv2')

    elbv2.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'id': instance_id} for instance_id instance_ids]
    )
    print("instances registered to target group successfully.")

def create_listener(load_balancer_arn,target_group_arn):
    elbv2= boto3.client('elbv2')
    elbv2.create_listener(
        LoadBalancerArn=load_balancer_arn,
        Protocol='HTTP'
        Port=80,
        DefaultActions=[{
            'Type':'forward',
            'TargetGroupArn':target_group_arn
        }]
    )
    print("listener created successfully.")

if __name__=="__main__":
    load_balancer_arn = deploy_alb()
    vpc_id = "your-vpc-id"
    target_group_arn= create_target_group(vpc_id)
    instance_ids=['instance-id-1','instance-id-2']

    load_balancer_arn
    register_targets(target_group_arn,instance_ids)
    create_listener(load_balancer_arn,target_group_arn)

