import json
import boto3
import uuid
from datetime import datetime

# Initialize clients
sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('EventHistory')

def lambda_handler(event, context):
    try:
        # 1. Parse Data
        body = json.loads(event['body'])
        event_name = body.get('event_name', 'Unnamed Event')
        details = body.get('details', 'No details provided')
        
        # 2. Create unique ID and Timestamp
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # 3. SAVE TO DYNAMODB
        table.put_item(
            Item={
                'EventID': event_id,
                'Timestamp': timestamp,
                'EventName': event_name,
                'Details': details
            }
        )

        # 4. SEND TO SNS
        TOPIC_ARN = "arn:aws:sns:ap-south-1:058264504117:EventAnnouncementTopic"
        sns_client.publish(
            TopicArn=TOPIC_ARN,
            Message=f"New Event: {event_name}\nDetails: {details}",
            Subject="New Event Announcement!"
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'Saved to Database & Sent!'})
        }

    except Exception as e:
        print(e)
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}