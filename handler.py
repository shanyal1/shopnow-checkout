import json
import random
import re
import time
import boto3

dynamodb = boto3.resource('dynamodb')
clicks_table = dynamodb.Table('shopnow-clicks')

VALID_PROMO_PATTERN = re.compile(r'^[A-Z0-9]{4,12}$')

def validate_promo_code(promo_code):
    """Validate promo_code: 4-12 uppercase alphanumeric characters."""
    if promo_code is None:
        return True, None
    if not isinstance(promo_code, str):
        return False, 'promo_code must be a string'
    if not VALID_PROMO_PATTERN.match(promo_code):
        return False, 'promo_code must be 4-12 uppercase alphanumeric characters'
    return True, None

def handler(event, context):
    time.sleep(random.uniform(0.05, 0.2))
    body = json.loads(event.get('body', '{}'))
    url = body.get('url', 'https://aws.amazon.com')

    # Validate promo_code if provided
    promo_code = body.get('promo_code')
    valid, error = validate_promo_code(promo_code)
    if not valid:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error})
        }

    code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))

    # Atomically increment click count
    resp = clicks_table.update_item(
        Key={'counterId': 'global'},
        UpdateExpression='ADD clicks :inc',
        ExpressionAttributeValues={':inc': 1},
        ReturnValues='UPDATED_NEW'
    )
    clicks = int(resp['Attributes']['clicks'])

    response = {
        'message': 'Payment processed successfully',
        'short_code': code,
        'url': url,
        'clicks': clicks
    }
    if promo_code:
        response['promo_code'] = promo_code

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
