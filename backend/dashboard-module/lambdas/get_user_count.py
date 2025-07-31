import boto3
import os
import json

dynamodb = boto3.resource("dynamodb")
users_table_name = os.environ.get("DYNAMODB_TABLE_NAME", "DALScooterUsers")
logins_table_name = os.environ.get("LOGIN_TABLE_NAME", "UserLogins")
users_table = dynamodb.Table(users_table_name)
logins_table = dynamodb.Table(logins_table_name)

def lambda_handler(event, context):
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

        # Scan UserLogins table for login activity
        login_response = logins_table.scan(
            Limit=100  # Limit to 100 recent logins to avoid excessive data
        )
        login_items = login_response.get("Items", [])

        # Handle pagination for logins
        while 'LastEvaluatedKey' in login_response:
            login_response = logins_table.scan(
                Limit=100,
                ExclusiveStartKey=login_response['LastEvaluatedKey']
            )
            login_items.extend(login_response.get("Items", []))

        # Sort logins by timestamp (newest first)
        login_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Format login activity for response
        login_activity = [
            {
                "user_id": item.get("user_id"),
                "timestamp": item.get("login_timestamp"),
                "success": item.get("success"),
                "message": item.get("message"),
                "ipAddress": item.get("ipAddress"),
                "userAgent": item.get("userAgent")
            }
            for item in login_items[:100]  # Ensure we return at most 100 records
        ]

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({
                "total_users": user_count,
                "login_activity": login_activity
            })
        }

    except Exception as e:
        print(f"Error in Lambda: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }