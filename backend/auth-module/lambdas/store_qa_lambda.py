import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

sqs = boto3.client('sqs')
QUEUE_URL = os.environ.get("REGISTRATION_QUEUE_URL")

sns = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

def handler(event, context):
    logger.info("Received event:")
    logger.info(json.dumps(event))

    try:
        body = json.loads(event['body'])
        logger.info(f"Parsed body: {body}")

        user_id = body['userId']
        question = body['question']
        answer = body['answer']
        email = body['email']
        role = body.get('role')  # Default to 'user' if not provided

        # Store in DynamoDB
        logger.info(f"Storing user info in DynamoDB for userId: {user_id}")
        table.put_item(Item={
            'userId': user_id,
            'email': email,
            'role': role,
            'securityQuestion': question,
            'securityAnswer': answer
        })

        # Subscribe email to SNS topic
        if SNS_TOPIC_ARN and email:
            logger.info(f"Subscribing {email} to SNS topic: {SNS_TOPIC_ARN}")
            sns.subscribe(
                TopicArn=SNS_TOPIC_ARN,
                Protocol="email",
                Endpoint=email,
                ReturnSubscriptionArn=True
            )

        # Send message to SQS for delayed welcome
        if QUEUE_URL:
            logger.info(f"Sending registration message to SQS queue: {QUEUE_URL}")
            sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps({
                    "email": email,
                    "type": "registration"
                })
            )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Q&A and role stored successfully. Confirmation email sent.'})
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
