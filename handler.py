import json
import random
import time

def handler(event, context):
    time.sleep(random.uniform(0.05, 0.2))
    body = json.loads(event.get('body', '{}'))
    url = body.get('url', 'https://aws.amazon.com')
    code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Payment processed successfully',
            'short_code': code,
            'url': url
        })
    }
