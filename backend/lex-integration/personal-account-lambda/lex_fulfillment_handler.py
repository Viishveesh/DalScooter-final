import json
import boto3
import os
from datetime import datetime

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Table names from environment variables
bookings_table = os.environ.get('BOOKINGS_TABLE_NAME', 'DALScooterBookings')
users_table = os.environ.get('USERS_TABLE_NAME', 'DALScooterUsers')

def lambda_handler(event, context):
    """
    Lex fulfillment handler for processing bot responses
    """
    try:
        # Extract information from the event
        intent_name = event.get('sessionState', {}).get('intent', {}).get('name')
        slots = event.get('sessionState', {}).get('intent', {}).get('slots', {})
        user_id = event.get('sessionState', {}).get('sessionAttributes', {}).get('userId')
        
        # Process the intent and generate response
        response_message = process_fulfillment(intent_name, slots, user_id)
        
        # Prepare the response
        response = {
            'sessionState': {
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Fulfilled'
                },
                'intent': {
                    'name': intent_name,
                    'state': 'Fulfilled'
                }
            },
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': response_message
                }
            ]
        }
        
        return response
        
    except Exception as e:
        return {
            'sessionState': {
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Failed'
                }
            },
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': f"I'm sorry, I encountered an error: {str(e)}"
                }
            ]
        }

def process_fulfillment(intent_name, slots, user_id):
    """
    Process different intents for fulfillment
    """
    if intent_name == 'BookScooter':
        return fulfill_book_scooter(slots, user_id)
    elif intent_name == 'CheckBooking':
        return fulfill_check_booking(user_id)
    elif intent_name == 'CancelBooking':
        return fulfill_cancel_booking(slots, user_id)
    elif intent_name == 'GetHelp':
        return "I can help you with booking scooters, checking your bookings, and canceling bookings. What would you like to do?"
    else:
        return "I'm here to help with your scooter rental needs. You can book a scooter, check your bookings, or cancel a booking. How can I assist you?"

def fulfill_book_scooter(slots, user_id):
    """Fulfill booking a scooter"""
    duration = slots.get('Duration', {}).get('value', {}).get('interpretedValue', '1 hour')
    location = slots.get('Location', {}).get('value', {}).get('interpretedValue', 'Unknown')
    
    try:
        # Create booking in DynamoDB
        table = dynamodb.Table(bookings_table)
        booking_id = f"BK{int(datetime.now().timestamp())}"
        
        booking_item = {
            'id': booking_id,
            'user_id': user_id,
            'location': location,
            'duration': duration,
            'status': 'confirmed',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        table.put_item(Item=booking_item)
        
        return f"I've successfully booked a scooter for you at {location} for {duration}. Your booking ID is {booking_id}. You can check your booking status anytime!"
        
    except Exception as e:
        return f"I'm sorry, I couldn't complete your booking at the moment. Please try again or contact support."

def fulfill_check_booking(user_id):
    """Fulfill checking booking status"""
    try:
        table = dynamodb.Table(bookings_table)
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        bookings = response.get('Items', [])
        if bookings:
            active_bookings = [b for b in bookings if b.get('status') == 'confirmed']
            if active_bookings:
                return f"You have {len(active_bookings)} active booking(s). The most recent is booking ID {active_bookings[0].get('id', 'Unknown')}."
            else:
                return "You don't have any active bookings at the moment."
        else:
            return "You don't have any bookings in our system."
    except Exception as e:
        return "I'm having trouble checking your bookings right now. Please try again later."

def fulfill_cancel_booking(slots, user_id):
    """Fulfill canceling a booking"""
    booking_id = slots.get('BookingId', {}).get('value', {}).get('interpretedValue', 'Unknown')
    
    try:
        # Update booking status in DynamoDB
        table = dynamodb.Table(bookings_table)
        
        # Check if booking exists and belongs to user
        response = table.get_item(
            Key={
                'id': booking_id,
                'user_id': user_id
            }
        )
        
        if 'Item' in response:
            # Update booking status
            table.update_item(
                Key={
                    'id': booking_id,
                    'user_id': user_id
                },
                UpdateExpression='SET #status = :status, updated_at = :updated_at',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'cancelled',
                    ':updated_at': datetime.now().isoformat()
                }
            )
            
            return f"I've successfully canceled your booking {booking_id}. You should receive a confirmation shortly."
        else:
            return f"I couldn't find booking {booking_id} in your account. Please check the booking ID and try again."
            
    except Exception as e:
        return f"I'm sorry, I couldn't cancel your booking at the moment. Please try again or contact support." 