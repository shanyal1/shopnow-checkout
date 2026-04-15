import json
import random
import time
import boto3

dynamodb = boto3.resource('dynamodb')
clicks_table = dynamodb.Table('shopnow-clicks')

def handler(event, context):
    time.sleep(random.uniform(0.05, 0.2))
    body = json.loads(event.get('body', '{}'))
    url = body.get('url', 'https://aws.amazon.com')
    code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))

    # Atomically increment click count
    resp = clicks_table.update_item(
        Key={'counterId': 'global'},
        UpdateExpression='ADD clicks :inc',
        ExpressionAttributeValues={':inc': 1},
        ReturnValues='UPDATED_NEW'
    )
    clicks = int(resp['Attributes']['clicks'])

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Payment processed successfully',
            'short_code': code,
            'url': url,
            'clicks': clicks
        })
    }
