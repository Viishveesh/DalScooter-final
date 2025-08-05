import json
import boto3
import os
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
cognito = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')

TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
USER_POOL_ID = os.environ['USER_POOL_ID']
DDB_TABLE_NAME = os.environ['USER_LOGINS_TABLE_NAME']

table = dynamodb.Table(DDB_TABLE_NAME)

def handler(event, context):
    try:
        logger.info("Received event:")
        logger.info(json.dumps(event))
        logger.info(f"Logging to DynamoDB table: {DDB_TABLE_NAME}")

        # This will actually be userId (sub), not the email
        user_id = event.get("email") or event.get("userEmail")
        if not user_id:
            raise ValueError("Missing userId (Cognito sub) in event payload.")

        # Fetching user's email from Cognito
        logger.info(f"Fetching email for Cognito userId: {user_id}")
        user = cognito.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=user_id
        )

        email_attr = next((attr['Value'] for attr in user['UserAttributes'] if attr['Name'] == 'email'), None)
        if not email_attr:
            raise ValueError("Email attribute not found for the user in Cognito.")

        # Send SNS notification
        message = f"Hello {email_attr}, your login to DALScooter was successful!"
        subject = "DALScooter Login Notification"

        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject=subject,
            Message=message
        )

        # Log login activity to DynamoDB
        login_time = datetime.utcnow().isoformat()

        table.put_item(
            Item={
                'user_id': user_id,
                'login_timestamp': login_time,
                'email': email_attr
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Login email sent and activity logged'})
        }

    except Exception as e:
        logger.error(f"Error handling login event: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
