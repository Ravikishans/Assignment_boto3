import boto3
import json

def create_sns_topics(config):
    sns = boto3.client('sns', region_name=config['region'])

    health_topic = sns.create_topic(Name='HealthAlerts')
    scaling_topic = sns.create_topic(Name='ScalingEvents')

    health_topic_arn = health_topic['TopicArn']
    scaling_topic_arn = scaling_topic['TopicArn']

    print(f"Health Alerts Topic ARN: {health_topic_arn}")
    print(f"Scaling Events Topic ARN: {scaling_topic_arn}")

    config.update({
        "health_topic_arn": health_topic_arn,
        "scaling_topic_arn": scaling_topic_arn
    })

    with open('config.json', 'w') as f:
        json.dump(config, f)

    return health_topic_arn, scaling_topic_arn

def subscribe_to_sns_topic(topic_arn, protocol, endpoint):
    sns = boto3.client('sns')

    sns.subscribe(
        TopicArn=topic_arn,
        Protocol=protocol,
        Endpoint=endpoint
    )
    print(f"Subscribed {endpoint} to {topic_arn} with {protocol} protocol.")

if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)

    health_topic_arn, scaling_topic_arn = create_sns_topics(config)

    subscribe_to_sns_topic(health_topic_arn, 'email', config['admin_email'])
    # subscribe_to_sns_topic(scaling_topic_arn, 'sms', config['admin_phone'])
