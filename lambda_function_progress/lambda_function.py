import json
import os
from twilio.rest import Client
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
                to=f'whatsapp:{whatsappid}'
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
    try:
        for record in event['Records']:
            # Extract relevant information from the stream record
            event_name = record['eventName']

            # Check if the event is MODIFY
            if event_name == 'MODIFY':
                new_image = record['dynamodb'].get('NewImage', {})  # Get the NewImage if available

                # Extract attribute values from NewImage
                new_image_values = {key: value['S'] for key, value in new_image.items()}

                # Show the value of 'response' field in NewImage
                response_value = new_image_values.get('supportresponse')
                username_value = new_image_values.get('username')
                whatsappif_value = new_image_values.get('whatsappid')
                progress_value = new_image_values.get('progress')
                text_message = f'Dear {username_value}, Thanks for your patience. Here is the latest update to your feedback. "{response_value}". And current status is: {progress_value}'
                # Print values if 'response' field is not None
                if response_value is not None:
                    send_whatsapp(text_message, whatsappif_value)
                    print("Value of 'response' field in NewImage:", response_value)
                    print("Value of 'username' field in NewImage:", username_value)
                    print("Value of 'whatsappid' field in NewImage:", whatsappif_value)

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'DynamoDB stream processed successfully'})
        }
    except Exception as e:
        # Handle any exceptions that occur during execution
        print('Error:', e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }