import boto3
from botocore.exceptions import ClientError

def create_vpc():
    ec2 = boto3.client('ec2')

    try:

        #creating vpc
        vpc_response = ec2.create_vpc(CidrBlock='10.0.0.0/16')
        vpc_id = vpc_response['Vpc']['VpcId']
        ec2.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': 'Boto3Assi'}])
        print(f"VPC '{vpc_id}' created successfully.")
        
        #creating subnets
        subnet1_response = ec2.create_subnet(CidrBlock='10.0.1.0/24', VpcId=vpc_id)
        subnet2_response = ec2.create_subnet(CidrBlock='10.0.2.0/24', VpcId=vpc_id)

        subnet1_id = subnet1_response['Subnet']['SubnetId']
        subnet2_id = subnet2_response['Subnet']['SubnetId']
        print(f"Subnets '{subnet1_id}' and '{subnet2_id}' created successfully.")

        #creating internet gateway
        igw_response = ec2.create_internet_gateway()
        igw_id = igw_response['InternetGateway']['InternetGatewayId']
        print(f"Internet gateway '{igw_id}' created successfully.")

        #attach Internet Gateway to VPC
        ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId= vpc_id)
        print(f"Internet gateway '{igw_id}' attached to VPC '{vpc_id}'. ")

        #Create Route Table
        route_table_response =ec2.create_route_table(VpcId=vpc_id)
        route_table_id = route_table_response['RouteTable']['RouteTableId']
        print(f"Route Table '{route_table_id}' created successfully.")

        #Create Route to Internet Gateway
        ec2.create_route(
            RouteTableId=route_table_id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw_id
        )
        print(f"Route to Internet Gateway '{igw_id} created successfully.")
        ec2.associate_route_table(SubnetId=subnet1_id, RouteTableId=route_table_id)
        ec2.associate_route_table(SubnetId=subnet2_id, RouteTableId=route_table_id)
        print(f"Route Table '{route_table_id} associated with subnets.")

        return vpc_id, subnet1_id, subnet2_id, igw_id, route_table_id
    
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

if __name__=="__main__":
    result = create_vpc()
    if result:
        vpc_id, subnet1_id, subnet2_id, igw_id, route_table_id = result
        print(f"Resources created successfully: VPC {vpc_id}, Subnets {subnet1_id}, {subnet2_id}, Internet Gateway {igw_id}, Route Table {route_table_id}")
    else:
        print("Failed to create resources.")