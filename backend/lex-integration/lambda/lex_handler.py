import json
import boto3
import os
from datetime import datetime

# Initialize AWS clients
lex_client = boto3.client('lexv2-runtime')
dynamodb = boto3.resource('dynamodb')

# Table names from environment variables
bookings_table = os.environ.get('BOOKINGS_TABLE_NAME', 'DALScooterBookings')
users_table = os.environ.get('USERS_TABLE_NAME', 'DALScooterUsers')

def lambda_handler(event, context):
    """
    Lambda handler for Lex integration
    Processes user messages and returns appropriate responses
    """
    try:
        # Parse the incoming event
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId')
        message = body.get('message')
        session_id = body.get('sessionId', f"session_{user_id}_{int(datetime.now().timestamp())}")
        
        # Prepare the request for Lex
        lex_request = {
            'botId': os.environ.get('LEX_BOT_ID'),
            'botAliasId': os.environ.get('LEX_BOT_ALIAS_ID'),
            'localeId': 'en_US',
            'sessionId': session_id,
            'text': message
        }
        
        # Call Lex
        lex_response = lex_client.recognize_text(**lex_request)
        
        # Process the response
        intent_name = lex_response.get('sessionState', {}).get('intent', {}).get('name')
        slots = lex_response.get('sessionState', {}).get('intent', {}).get('slots', {})
        
        # Generate response based on intent
        response_message = process_intent(intent_name, slots, user_id)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'message': response_message,
                'intent': intent_name,
                'slots': slots,
                'sessionId': session_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def process_intent(intent_name, slots, user_id):
    """
    Process different intents and return appropriate responses
    """
    if intent_name == 'BookScooter':
        return process_book_scooter(slots, user_id)
    elif intent_name == 'CheckBooking':
        return process_check_booking(user_id)
    elif intent_name == 'CancelBooking':
        return process_cancel_booking(slots, user_id)
    elif intent_name == 'GetHelp':
        return "I can help you with booking scooters, checking your bookings, and canceling bookings. What would you like to do?"
    else:
        return "I'm here to help with your scooter rental needs. You can book a scooter, check your bookings, or cancel a booking. How can I assist you?"

def process_book_scooter(slots, user_id):
    """Process booking a scooter"""
    duration = slots.get('Duration', {}).get('value', {}).get('interpretedValue', '1 hour')
    location = slots.get('Location', {}).get('value', {}).get('interpretedValue', 'Unknown')
    
    # Here you would integrate with your booking system
    booking_id = f"BK{int(datetime.now().timestamp())}"
    
    return f"I've booked a scooter for you at {location} for {duration}. Your booking ID is {booking_id}. You can check your booking status anytime!"

def process_check_booking(user_id):
    """Process checking booking status"""
    try:
        table = dynamodb.Table(bookings_table)
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        bookings = response.get('Items', [])
        if bookings:
            return f"You have {len(bookings)} active booking(s). The most recent is booking ID {bookings[0].get('id', 'Unknown')}."
        else:
            return "You don't have any active bookings at the moment."
    except Exception as e:
        return "I'm having trouble checking your bookings right now. Please try again later."

def process_cancel_booking(slots, user_id):
    """Process canceling a booking"""
    booking_id = slots.get('BookingId', {}).get('value', {}).get('interpretedValue', 'Unknown')
    
    # Here you would integrate with your booking cancellation system
    return f"I've canceled your booking {booking_id}. You should receive a confirmation shortly." 