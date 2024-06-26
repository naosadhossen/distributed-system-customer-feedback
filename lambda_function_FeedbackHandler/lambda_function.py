import json
import boto3
from twilio.rest import Client
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
import time
from twilio.base.exceptions import TwilioRestException

def send_whatsapp(text_message, recepient):
    response_message = text_message
    whatsappid = recepient
    account_sid = os.environ.get('account_sid')
    auth_token = os.environ.get(account_sid)
    client = Client(account_sid, auth_token)
    max_retry_attempts = 10
    retry_delay_seconds = 5
    for attempt in range(1, max_retry_attempts + 1):
        try:
            message = client.messages.create(
                from_='whatsapp:+14155238886',
                body=response_message,
                to=f'whatsapp:{whatsappid}',
                attempt=10
            )
            print("WhatsApp message sent successfully.")
            break  # Exit the loop if message sent successfully
        except TwilioRestException as e:
            print(f"Error sending WhatsApp message (attempt {attempt}):", e)
            if attempt < max_retry_attempts:
                print(f"Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
    else:
        print("Failed to send WhatsApp message after multiple attempts.")


def lambda_handler(event, context):
    # Extract text from the body of the API Gateway request
    body = json.loads(event['body'])
    feedback = body['text']
    user = body['username']
    whatsappid = body['whatsappid']
    # Call detect_sentiment API of AWS Comprehend
    comprehend = boto3.client('comprehend')
    dynamodb = boto3.client('dynamodb')
    response = comprehend.detect_sentiment(Text=feedback, LanguageCode='en')
    sentiment = response['Sentiment']

    # Save data in db
    serviceid = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    item = {
        'id': {'S': serviceid},
        'username': {'S': user},
        'whatsappid': {'S': whatsappid},
        'feedback': {'S': feedback},
        'timestamp': {'S': timestamp},
        'sentiment': {'S': sentiment},
        'progress': {'S': 'Open'}
    }
    # Call DynamoDB put_item method
    try:
        dynamodb.put_item(TableName='feedback', Item=item)
        if sentiment == 'POSITIVE':
            response_message = (f'Dear {user}, We are happy to see that our service has found your appreciation. '
                                f'We will review your feedback in deatils and get back to you if any follow up action is required.')
            send_whatsapp(response_message, whatsappid)

        elif sentiment == 'NEGATIVE':
            response_message = f'Dear {user}, We regret to see that your are not satisfied with our service. We always take customer feedback seriously. We will review your feedback and get back to you soon.'
            send_whatsapp(response_message, whatsappid)
        elif sentiment == 'NEUTRAL':
            response_message = f'Dear {user}, Thanks for your feedback. We will review and get back to you if any follow up action is required.'
            send_whatsapp(response_message, whatsappid)
        elif sentiment == 'MIXED':
            response_message = f'Dear {user}, Thanks for your feedback. We will review and get back to you if any follow up action is required.'
            send_whatsapp(response_message, whatsappid)
        else:
            response_message = f'Dear {user}, Thanks for your feedback. We will review and get back to you if any follow up action is required.'
            send_whatsapp(response_message, whatsappid)
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': 'Feedback received and processed'})
        }

    except Exception as e:
        print(f"Error handling feedback: {e}")
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
