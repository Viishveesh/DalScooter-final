import json
import boto3
from datetime import datetime
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('USERS_TABLE_NAME', 'DALScooterUsers')

def lambda_handler(event, context):
    """
    Lambda function to get user count for dashboard
    """
    try:
        table = dynamodb.Table(table_name)
        
        # Get total user count
        response = table.scan(
            Select='COUNT'
        )
        
        total_users = response['Count']
        
        # Get active users (users who have logged in recently)
        current_time = datetime.utcnow().isoformat()
        response = table.scan(
            FilterExpression='attribute_exists(last_login)',
            Select='COUNT'
        )
        
        active_users = response['Count']
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'total_users': total_users,
                'active_users': active_users,
                'timestamp': current_time
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }