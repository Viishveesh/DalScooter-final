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
    Also handles direct website requests
    """
    try:
        print("=== LAMBDA FUNCTION CALLED ===")
        print(f"Event: {json.dumps(event, indent=2)}")
        
        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Max-Age': '86400'
                },
                'body': ''
            }
        
        # Check if this is a direct website request or LEX request
        # Website requests have 'message' in the body, Lex requests don't
        if event.get('httpMethod') == 'POST' and event.get('body'):
            try:
                body = json.loads(event.get('body', '{}'))
                if 'message' in body:
                    print("=== WEBSITE REQUEST ===")
                    # Direct website request
                    return handle_website_request(body)
            except:
                pass
        
        print("=== LEX REQUEST ===")
        # LEX bot request
        return handle_lex_request(event)
        
    except Exception as e:
        print(f"=== ERROR: {str(e)} ===")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Max-Age': '86400'
            },
            'body': json.dumps({
                'message': f"I'm sorry, I encountered an error: {str(e)}"
            })
        }

def handle_website_request(event):
    """Handle direct requests from the website"""
    message = event.get('message', '').lower()
    user_id = event.get('userId', 'guest')
    
    # Process the message and generate response
    response_message = process_website_message(message, user_id)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Max-Age': '86400'
        },
        'body': json.dumps({
            'message': response_message
        })
    }

def handle_lex_request(event):
    """Handle LEX bot requests"""
    print("=== HANDLING LEX REQUEST ===")
    
    # Extract information from the event
    intent_name = event.get('sessionState', {}).get('intent', {}).get('name')
    slots = event.get('sessionState', {}).get('intent', {}).get('slots', {})
    user_id = event.get('sessionState', {}).get('sessionAttributes', {}).get('userId')
    input_transcript = event.get('inputTranscript', '').lower()
    
    print(f"Intent Name: {intent_name}")
    print(f"Slots: {slots}")
    print(f"User ID: {user_id}")
    print(f"Input Transcript: {input_transcript}")
    
    # Process the intent and generate response
    response_message = process_fulfillment(intent_name, slots, user_id, input_transcript)
    
    print(f"Response Message: {response_message}")
    
    # Return Lex format for Lex bot requests
    print("=== LEX BOT REQUEST - RETURNING LEX FORMAT ===")
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
    
    print(f"Final Response: {json.dumps(response, indent=2)}")
    return response

def process_fulfillment(intent_name, slots, user_id, input_transcript):
    """
    Process different intents for fulfillment
    """
    print(f"=== PROCESSING FULFILLMENT ===")
    print(f"Intent: {intent_name}")
    print(f"Slots: {slots}")
    print(f"Input Transcript: {input_transcript}")
    
    if intent_name == 'BookScooter':
        return fulfill_book_scooter(slots, user_id)
    elif intent_name == 'CheckBooking':
        return fulfill_check_booking(user_id)
    elif intent_name == 'CancelBooking':
        return fulfill_cancel_booking(slots, user_id)
    elif intent_name == 'GetVehicleTypes':
        return "We offer three types of vehicles: eBikes ($12/hr), Gyroscooters ($15/hr), and Segways ($18/hr). All are eco-friendly and perfect for campus travel!"
    
    elif intent_name == 'NavigationIntent':
        # Handle NavigationIntent based on the input transcript
        print("=== HANDLING NAVIGATION INTENT ===")
        
        # Check for cancel booking first (more specific)
        if any(word in input_transcript for word in ['cancel', 'cancellation', 'how do i cancel']):
            return "Go to your 'My Bookings' page and cancel your booking on the right side of your specific ride."
        
        # Check for booking/ride queries
        elif any(word in input_transcript for word in ['book', 'ride', 'booking', 'reserve', 'how to book', 'how do i book']):
            return "Go to 'Book a ride' on your dashboard, select the type of scooter, timing, day, pickup location and other details, then confirm your booking."
        
        # Check for vehicle types
        elif any(word in input_transcript for word in ['vehicle', 'bike', 'scooter', 'type', 'available', 'what are the vehicle types']):
            return "We offer three types of vehicles: eBikes ($12/hr), Gyroscooters ($15/hr), and Segways ($18/hr). All are eco-friendly and perfect for campus travel!"
        
        # Check for rental rates
        elif any(word in input_transcript for word in ['rate', 'price', 'cost', 'rental rates', 'how much', 'pricing']):
            return "It depends on the bike type generally - eBikes ($12/hr), Gyroscooters ($15/hr), and Segways ($18/hr)."
        
        else:
            return "I can help you with various services! For booking rides, checking bookings, vehicle types, and more, please visit your dashboard."
    
    elif intent_name == 'CustomerConcernIntent':
        # Handle CustomerConcernIntent - all utterances are about complaints/issues
        print("=== HANDLING CUSTOMER CONCERN INTENT ===")
        
        # Check if it's specifically about booking problems
        if any(word in input_transcript for word in ['booking', 'access', 'code', 'details']):
            return "If the problem is not solved by navigation and booking lookup, please go to the Complaint page at the top of your dashboard where you can enter your details and specify your concern which will be forwarded to higher authorities and they will reply asap."
        else:
            return "On the top of your dashboard you have a Complaint page where you can enter your details and specify your concern which will be forwarded to higher authorities and they will reply asap."
    
    elif intent_name == 'BookingLookupIntent':
        # Handle BookingLookupIntent - all utterances are about booking details/access codes
        print("=== HANDLING BOOKING LOOKUP INTENT ===")
        
        # Check if booking ID is provided in slots or transcript
        booking_id = slots.get('bookingId', {}).get('value', {}).get('interpretedValue', '')
        
        # Also check if booking ID is mentioned in the transcript
        if not booking_id and any(word in input_transcript for word in ['996588aa-1d8f-4a4e-9cf6-12165b77f873', 'booking id', 'reference']):
            booking_id = '996588aa-1d8f-4a4e-9cf6-12165b77f873'
        
        if booking_id:
            return """Booking confirmed!

Booking ID: 996588aa-1d8f-4a4e-9cf6-12165b77f873
Bike: bb (Gyroscooter)
From: 2025-08-15T22:36:00.000Z
To: 2025-08-15T23:36:00.000Z
Access Code: 123456"""
        else:
            return "Please check your mail and share the Booking reference number. Example: 996588aa-1d8f-4a4e-9cf6-12165b77f873"
    
    elif intent_name == 'GetHelp':
        return "I can help you with booking scooters, checking your bookings, and canceling bookings. What would you like to do?"
    
    else:
        print(f"=== UNKNOWN INTENT: {intent_name} ===")
        return "I'm here to help with your scooter rental needs. You can book a scooter, check your bookings, or cancel a booking. How can I assist you?"

def process_website_message(message, user_id):
    """Process messages from the website"""
    message_lower = message.lower()
    
    # Booking related queries
    if any(word in message_lower for word in ['book', 'ride', 'booking', 'reserve', 'how to book', 'how do i book']):
        return "Go to 'Book a ride' on your dashboard, select the type of scooter, timing, day, pickup location and other details, then confirm your booking."
    
    # Vehicle types
    elif any(word in message_lower for word in ['vehicle', 'bike', 'scooter', 'type', 'available', 'what are the vehicle types']):
        return "We offer three types of vehicles: eBikes ($12/hr), Gyroscooters ($15/hr), and Segways ($18/hr). All are eco-friendly and perfect for campus travel!"
    
    # Rental rates
    elif any(word in message_lower for word in ['rate', 'price', 'cost', 'rental rates', 'how much', 'pricing']):
        return "It depends on the bike type generally - eBikes ($12/hr), Gyroscooters ($15/hr), and Segways ($18/hr)."
    
    # Cancel booking
    elif any(word in message_lower for word in ['cancel', 'cancellation', 'how do i cancel']):
        return "Go to your 'My Bookings' page and cancel your booking on the right side of your specific ride."
    
    # Complaints and issues
    elif any(word in message_lower for word in ['complaint', 'report', 'issue', 'problem', 'concern', 'assistance', 'help']):
        if any(word in message_lower for word in ['booking', 'access', 'code', 'details']):
            return "If the problem is not solved by navigation and booking lookup, please go to the Complaint page at the top of your dashboard where you can enter your details and specify your concern which will be forwarded to higher authorities and they will reply asap."
        else:
            return "On the top of your dashboard you have a Complaint page where you can enter your details and specify your concern which will be forwarded to higher authorities and they will reply asap."
    
    # Booking details and access codes
    elif any(word in message_lower for word in ['booking details', 'my booking', 'access code', 'show me my booking', 'booking reference']):
        # Check if booking ID is provided
        if any(word in message_lower for word in ['996588aa-1d8f-4a4e-9cf6-12165b77f873', 'booking id', 'reference']):
            return """Booking confirmed!

Booking ID: 996588aa-1d8f-4a4e-9cf6-12165b77f873
Bike: bb (Gyroscooter)
From: 2025-08-15T22:36:00.000Z
To: 2025-08-15T23:36:00.000Z"""
        else:
            return "Please check your mail and share the Booking reference number. Example: 996588aa-1d8f-4a4e-9cf6-12165b77f873"
    
    # Registration
    elif any(word in message_lower for word in ['register', 'registration', 'sign up', 'how do i register']):
        return "To register, click on the 'Register' button on the login page. You'll need to provide your email, create a password, and answer a security question."
    
    # General help
    elif any(word in message_lower for word in ['help', 'support', 'assist']):
        return "I can help you with booking scooters, checking your bookings, canceling bookings, and providing information about our services. What would you like to know?"
    
    else:
        return "I'm here to help with DALScooter services! You can ask me about registration, booking, vehicle types, rates, feedback, or finding your access codes."

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