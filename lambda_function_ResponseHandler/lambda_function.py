import json
import boto3

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    # Parse the request body to extract ID and new value
    body = json.loads(event['body'])
    print(body)
    body_id = body.get('id')
    print(body_id)
    body_new_response_value = body.get('newresponse')
    print(body_new_response_value)
    body_whatsappid=body.get('whatsappid')
    print(body_whatsappid)

    # Check if ID and new value are provided
    if not body_id or not body_new_response_value or not body_whatsappid:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'ID and new value are required'})
        }

    try:
        # Retrieve the current value of the attribute
        current_response = dynamodb.get_item(
            TableName='feedback',
            Key={
                'id': {'S': body_id},
                'whatsappid': {'S': body_whatsappid}
            },
            ProjectionExpression='supportresponse'
        )
        current_response_value = current_response.get('Item', {}).get('supportresponse', {'S': ''})['S']
        print(current_response_value)

        # Concatenate the new value with the current value
        updated_response_value = current_response_value + body_new_response_value
        print(updated_response_value)

        # Update the attribute in DynamoDB
        dynamodb.update_item(
            TableName='feedback',
            Key={
                'id': {'S': body_id},
                'whatsappid': {'S': body_whatsappid}
            },
            UpdateExpression='SET supportresponse = :val',
            ExpressionAttributeValues={':val': {'S': updated_response_value}}
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Attribute updated successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
