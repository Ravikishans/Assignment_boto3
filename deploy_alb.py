import boto3
import json

def deploy_alb(config):
    elbv2 = boto3.client('elbv2', region_name=config['region'])

    load_balancer = elbv2.create_load_balancer(
        Name='my-load-balancer',
        Subnets=[config['subnet1_id'], config['subnet2_id']],
        SecurityGroups=[config['security_group_id']],
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4'
    )
    load_balancer_arn = load_balancer['LoadBalancers'][0]['LoadBalancerArn']
    print(f"ALB '{load_balancer_arn}' created successfully.")
    return load_balancer_arn

def create_target_group(config):
    elbv2 = boto3.client('elbv2', region_name=config['region'])

    target_group = elbv2.create_target_group(
        Name='my-target-group',
        Protocol='HTTP',
        Port=80,
        VpcId=config['vpc_id'],
        HealthCheckProtocol='HTTP',
        HealthCheckPort='80',
        HealthCheckPath='/',
        TargetType='instance'
    )
    target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']
    print(f"Target group '{target_group_arn}' created successfully.")
    return target_group_arn

def register_targets(config, target_group_arn):
    elbv2 = boto3.client('elbv2', region_name=config['region'])

    elbv2.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'Id': instance_id} for instance_id in config['instance_ids']]
    )
    print("Instances registered to target group successfully.")

def create_listener(load_balancer_arn, target_group_arn, config):
    elbv2 = boto3.client('elbv2', region_name=config['region'])

    elbv2.create_listener(
        LoadBalancerArn=load_balancer_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[{
            'Type': 'forward',
            'TargetGroupArn': target_group_arn
        }]
    )
    print("Listener created successfully.")

if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)

    load_balancer_arn = deploy_alb(config)
    target_group_arn = create_target_group(config)
    register_targets(config, target_group_arn)
    create_listener(load_balancer_arn, target_group_arn, config)
    
    config.update({
        "load_balancer_arn": load_balancer_arn,
        "target_group_arn": target_group_arn
    })

    with open('config.json', 'w') as f:
        json.dump(config, f)
