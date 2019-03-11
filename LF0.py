import json
import time
import botocore.session

session = botocore.session.get_session()
client = session.create_client('lex-runtime')
userid = str(int(time.time()))

def lambda_handler(event, context):
    # TODO implement
    msg = event['messages'][0]['unstructured']['text']
    response = client.post_text(
        botName='DiningConcierge',
        botAlias='DiningConcierge',
        userId=userid,
        inputText= msg
        )
    print(response['message'])
    
    return {
        'statusCode': 200,
        'messages': [{
            'type':"string",
            'unstructured': {
                'type':"string",
                'text':response['message'],
                'timestamp':str(time.time())
            }
        }
            
            ]
    }
