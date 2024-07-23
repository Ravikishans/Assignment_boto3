import boto3
import json

def create_vpc():
    ec2 = boto3.client('ec2')

    vpc_response = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc_response['Vpc']['VpcId']
    ec2.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': 'Boto3Assi'}])

    print(f"VPC '{vpc_id}' created successfully.")

    # Describe availability zones
    availability_zones = ec2.describe_availability_zones()['AvailabilityZones']

    subnet1_response = ec2.create_subnet(
        CidrBlock='10.0.1.0/24', 
        VpcId=vpc_id, 
        AvailabilityZone=availability_zones[0]['ZoneName']
    )
    subnet2_response = ec2.create_subnet(
        CidrBlock='10.0.2.0/24', 
        VpcId=vpc_id, 
        AvailabilityZone=availability_zones[1]['ZoneName']
    )
    subnet1_id = subnet1_response['Subnet']['SubnetId']
    subnet2_id = subnet2_response['Subnet']['SubnetId']
    print(f"Subnets '{subnet1_id}' and '{subnet2_id}' created successfully.")

    igw_response = ec2.create_internet_gateway()
    igw_id = igw_response['InternetGateway']['InternetGatewayId']
    print(f"Internet Gateway '{igw_id}' created successfully.")

    ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print(f"Internet Gateway '{igw_id}' attached to VPC '{vpc_id}'.")

    route_table_response = ec2.create_route_table(VpcId=vpc_id)
    route_table_id = route_table_response['RouteTable']['RouteTableId']
    print(f"Route Table '{route_table_id}' created successfully.")

    ec2.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id
    )
    print(f"Route to Internet Gateway '{igw_id}' created successfully.")

    ec2.associate_route_table(SubnetId=subnet1_id, RouteTableId=route_table_id)
    ec2.associate_route_table(SubnetId=subnet2_id, RouteTableId=route_table_id)
    print(f"Route Table '{route_table_id}' associated with subnets.")

    # Create a security group within the VPC
    security_group_response = ec2.create_security_group(
        GroupName='web-server-sg',
        Description='Security group for web server',
        VpcId=vpc_id
    )
    security_group_id = security_group_response['GroupId']
    print(f"Security Group '{security_group_id}' created successfully within VPC '{vpc_id}'.")

    # Allow inbound traffic on port 80 (HTTP) and 22 (SSH)
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
    print("Ingress rules added to the security group.")


    with open('config.json') as f:
        config = json.load(f)
    
    config.update({
        "vpc_id": vpc_id,
        "subnet1_id": subnet1_id,
        "subnet2_id": subnet2_id,
        "igw_id": igw_id,
        "route_table_id": route_table_id,
        "security_group_id": security_group_id
    })

    with open('config.json', 'w') as f:
        json.dump(config, f)

if __name__ == "__main__":
    create_vpc()
