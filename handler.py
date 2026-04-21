import json
import random
import re
import time
import uuid
from datetime import datetime, timezone
import boto3

dynamodb = boto3.resource('dynamodb')
clicks_table = dynamodb.Table('shopnow-clicks')
click_events_table = dynamodb.Table('shopnow-click-events')

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

    # Record individual click event for tracking
    click_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    request_context = event.get('requestContext', {})
    identity = request_context.get('identity', {})

    click_event = {
        'clickId': click_id,
        'timestamp': timestamp,
        'url': url,
        'shortCode': code,
        'sourceIp': identity.get('sourceIp', 'unknown'),
        'userAgent': identity.get('userAgent', 'unknown'),
    }
    if promo_code:
        click_event['promoCode'] = promo_code

    click_events_table.put_item(Item=click_event)

    # Memorial Day promotion: 20% off orders over $50
    order_total = body.get('order_total', 0)
    try:
        order_total = float(order_total)
    except (TypeError, ValueError):
        order_total = 0

    promo = {
        'name': 'Memorial Day Sale',
        'description': '20% off orders over $100',
        'code': 'MEMORIAL20',
        'min_order': 100,
        'discount_pct': 20,
        'applied': False,
        'discount_amount': 0,
        'final_total': order_total
    }

    if order_total > 100 and promo_code == 'MEMORIAL20':
        discount = round(order_total * 0.20, 2)
        promo['applied'] = True
        promo['discount_amount'] = discount
        promo['final_total'] = round(order_total - discount, 2)

    response = {
        'message': 'Payment processed successfully',
        'short_code': code,
        'click_id': click_id,
        'url': url,
        'clicks': clicks,
        'promo': promo
    }
    if promo_code:
        response['promo_code'] = promo_code

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
