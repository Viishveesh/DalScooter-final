import json
import boto3
from datetime import datetime
import os

dynamodb = boto3.resource("dynamodb")
users_table_name = os.environ.get("DYNAMODB_TABLE_NAME", "DALScooterUsers")
logins_table_name = os.environ.get("LOGIN_TABLE_NAME", "UserLogins")
bookings_table_name = os.environ.get("BOOKINGS_TABLE_NAME", "DALScooterBookings")
users_table = dynamodb.Table(users_table_name)
logins_table = dynamodb.Table(logins_table_name)
bookings_table = dynamodb.Table(bookings_table_name)

def lambda_handler(event, context):
    """
    Lambda function to get user count for dashboard
    """
    try:
        # Scan DALScooterUsers table for users with role = "user"
        response = users_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("role").eq("user")
        )
        user_count = len(response.get("Items", []))

        # Handle pagination for users
        while 'LastEvaluatedKey' in response:
            response = users_table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("role").eq("user"),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            user_count += len(response.get("Items", []))

        # Scan DALScooterBookings table for bookings with status = "active"
        bookings_response = bookings_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("status").eq("active")
        )
        active_bookings_count = len(bookings_response.get("Items", []))

        # Handle pagination for bookings
        while 'LastEvaluatedKey' in bookings_response:
            bookings_response = bookings_table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("status").eq("active"),
                ExclusiveStartKey=bookings_response['LastEvaluatedKey']
            )
            active_bookings_count += len(bookings_response.get("Items", []))

        # Scan UserLogins table for login activity
        login_response = logins_table.scan(
            Limit=100  # Limit to 100 recent logins to avoid excessive data
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            "body": json.dumps({
                "total_users": user_count,
                "total_active_bookings": active_bookings_count,
                "login_activity": login_response
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