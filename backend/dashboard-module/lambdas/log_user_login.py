import json
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("UserLogins")

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    body = json.loads(event["body"])
    
    user_id = body.get("username")  # Map frontend's "username" to "user_id"
    success = body.get("success")
    message = body.get("message")
    timestamp = datetime.utcnow().isoformat()

    item = {
        "user_id": user_id,  # Use "user_id" to match the table's partition key
        "login_timestamp": timestamp,
        "success": success,
        "message": message,
    }
    print(f"Writing item to DynamoDB: {item}")

    try:
        table.put_item(Item=item)
        print("Successfully wrote to DynamoDB")
    except Exception as e:
        print(f"Error writing to DynamoDB: {str(e)}")
        raise e

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Login log stored successfully"})
    }