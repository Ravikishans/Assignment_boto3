# Infrastructure Management

This repository contains scripts to automatically manages the lifecycle of a web application hosted on  EC2 instances, monitors its health, and reacts to changes in traffic by scaling resources.  Furthermore, administrators receive notifications regarding the infrastructure's health and scaling events. 


## Getting Started

### Prerequisites

- Python 3.x
- Boto3 library
- AWS credentials configured (either through AWS CLI or environment variables)

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/Ravikishans/Assignment_boto3.git
    ```

2. Update the `config.json` file with your AWS details:

    ```json
    {
      "bucket_name": "your-bucket-name",
      "region": "your-region",
      "key_pair_name": "your-key-pair-name",
      "security_group_id": "your-security-group-id",
      "admin_email": "your-email@example.com"
    }
    ```

## Usage

### Deploying the Infrastructure

To deploy the infrastructure, run:

```sh
python manageInfra.py deploy
```

### Updating the Infrastructure

To update the infrastructure, run:

```sh
python manageInfra.py update
```

### Tearing Down the Infrastructure

To tear down the infrastructure, run:

```sh
python manageInfra.py teardown
```

## Scripts Description

### `create_asg.py`

Creates an Auto Scaling Group based on the configurations provided.

### `create_s3_bucket.py`

Creates an S3 bucket with the specified name.

### `create_vpc.py`

Creates a Virtual Private Cloud (VPC) and the associated subnets, internet gateways, and route tables.

### `deploy_alb.py`

Deploys an Application Load Balancer and configures the necessary listeners and target groups.

### `launch_ec2_instance.py`

Launches an EC2 instance using the specified AMI, instance type, key pair, and security group.

### `setup_sns_notifications.py`

Sets up SNS notifications and subscribes the provided email address to the notifications.

### `manageInfra.py`

Main script to manage the deployment, update, and teardown of the entire infrastructure.

---

Feel free to customize any sections as per your specific repository details and requirements.
