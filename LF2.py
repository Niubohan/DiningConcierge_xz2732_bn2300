import json
import boto3
from botocore.vendored import requests

topic_arn = ''
es_domian = ''


def lambda_handler(event, context):
    # TODO implement
    
    """ --- Fetch SQS--- """
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='hw2')
    message = queue.receive_messages(MessageAttributeNames=[
        'Cuisine','Num_people','Date','Time','Phone'
        ])
    
    while len(message):
        info = message[0].message_attributes
        cuisine, num_people, date, time, phone = info['Cuisine']['StringValue'], info['Num_people']['StringValue'],\
        info['Date']['StringValue'], info['Time']['StringValue'], info['Phone']['StringValue']
        
        """ --- Query in ES --- """
        url = es_domian + '/_search?q=Cuisine:{}&size=3&sort=Score:desc'.format(cuisine.lower())
        es_response = requests.request('GET', url).json()
        rst_ids = [es_response['hits']['hits'][i]['_id'] for i in range(3)]
        print(rst_ids)
        
        """ --- Query in DB --- """
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('yelp-restaurants')
        responses = [table.get_item(Key={'Business ID': rst_ids[i]}) for i in range(3)]
        rst_info = ", ".join(["{}. {}, located at {}".format(i, item['Item']['Name'], item['Item']['Address']) for i, item in enumerate(responses, 1)])
        print(rst_info)
        
        """ --- Send SNS --- """
        sms_msg = 'Here are my {} restaurant suggestions for {} people, for {} at {}: {}. Enjoy your meal!'.format(cuisine, num_people, date, time, rst_info)
        sns = boto3.resource('sns')
        topic = sns.Topic('hw2')
        topic.subscribe(
            TopicArn=topic_arn,
            Protocol='sms',
            Endpoint='+1'+phone 
        )
        topic.publish(Message=sms_msg, TopicArn=topic_arn)
        
        message[0].delete()
        message = queue.receive_messages(MessageAttributeNames=[
        'Cuisine','Num_people','Date','Time','Phone'
        ])
        if len(message): break
    
    return {
        'statusCode': 200,
        'body': json.dumps('SQS handled!')
    }
