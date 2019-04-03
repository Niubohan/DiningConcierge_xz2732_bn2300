import math
import dateutil.parser
import datetime
import time
import os
import logging
import json
from botocore.vendored import requests 
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """
def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')
        

def isvalid_cuisine(cusinie):
    valid_cuisines = ['brazilian', 'british', 'chinese', 'filipino', 'french',
    'greek', 'indian', 'irish', 'italian', 'jamaican', 'japanese', 'korean', 
    'mexican', 'moroccan', 'russian', 'ameriacan', 'spanish', 'thai','vietnamese']
    return cusinie.lower() in valid_cuisines

def isvalid_city(city):
    valid_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland','manhattan']
    return city.lower() in valid_cities


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False
        

def isvalid_time(time):
    if len(time) != 5:
        return False
    return True


def isvalid_phone(phone):
    if len(phone) == 10 and phone.isdigit():
        return True
    return False
    

def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_infor(slots):
    input_loc = try_ex(lambda: slots['Location'])
    input_cus = try_ex(lambda: slots['Cuisine'])
    input_date = try_ex(lambda: slots['Date'])
    input_time = try_ex(lambda: slots['Time'])
    input_num = try_ex(lambda: slots['Num_people'])
    input_phone = try_ex(lambda: slots['Phone'])

    if input_loc and not isvalid_city(input_loc):
        return build_validation_result(
            False,
            'Location',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(input_loc)
        )
        
    if input_cus:
        if not isvalid_cuisine(input_cus):
            return build_validation_result(
                False, 
                'Cuisine', 
                'We currently do not support {} as a valid cusinie. Can you try a different cusinie?'.format(input_cus)
            )

    if input_date:
        if not isvalid_date(input_date):
            return build_validation_result(
                False, 
                'Date', 
                'I did not understand your date. When would you like to go to the restaurant?')

    if input_time:
        if not isvalid_time(input_time):
            return build_validation_result(
                False, 
                'Time', 
                'I did not understand your time. When would you like to go to the restaurant?')
    
    if input_num:
        if parse_int(input_num) == float('nan'):
            return build_validation_result(
                False, 
                'Num_people', 
                'I did not understand your input. How many people will go to the restaurant?')
    
    if input_phone:
        if not isvalid_time(input_time):
            return build_validation_result(
                False, 
                'Phone', 
                'The input is not in the correct format, please enter again.')
    
    return {'isValid': True}

""" --- Yelp API function --- """

API_Key = "RlUbZiSt-625bnIjp6GLxtcftyozA7DcvcRGv0UV-welvziCGqkLu9E3ASePy5S04_19vcOSd7NYkx9hNgtcpbVKYWPo8Ib6hFG0k8Lb7GcliyQydpTt9M-LwK1-XHYx"

def yelp_search(location, cusinie, date, dinning_time):
    headers = {
        'Authorization': 'Bearer %s' % API_Key,
    }
    res = []
    time_array = time.strptime(date + " " + dinning_time, "%Y-%m-%d %H:%M")
    time_stamp = int(time.mktime(time_array))
    url = "https://api.yelp.com/v3/businesses/search?location={}&categories={}&limit=3&open_at={}".format(location, cusinie, time_stamp)
    api_response = requests.request('GET', url, headers=headers).json()
    for i, restaurant in enumerate(api_response['businesses'],1):
        res_str = "{}. {}, located at {}".format(str(i), restaurant['name'], restaurant['location']['address1'])
        res.append(res_str)
    return ", ".join(res)
    


""" --- Functions that control the bot's behavior --- """


def dinning_suggest(intent_request):

    location = get_slots(intent_request)["Location"]
    cusinie_type = get_slots(intent_request)["Cuisine"]
    date = get_slots(intent_request)["Date"]
    dinning_time = get_slots(intent_request)["Time"]
    num_people = get_slots(intent_request)['Num_people']
    phone = get_slots(intent_request)['Phone']
    
    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_infor(intent_request['currentIntent']['slots'])

        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
         
        return delegate(output_session_attributes, intent_request['currentIntent']['slots'])
        
    # api_res = yelp_search(location.lower(), cusinie_type.lower(), date, dinning_time)
    
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='hw2')
    
    msg = {
        'Cuisine': {
            'StringValue': cusinie_type,
            'DataType': 'String'
        },
        'Num_people': {
            'StringValue': num_people,
            'DataType': 'String'
        },
        'Date': {
            'StringValue': date,
            'DataType': 'String'
        },
        'Time': {
            'StringValue': dinning_time,
            'DataType': 'String'
        },
        'Phone': {
            'StringValue': phone,
            'DataType': 'String'
        }
    }
    
    queue.send_message(MessageBody='message', MessageAttributes=msg)
    """return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Here are my {} restaurant suggestions for {} people, for {} at {}: {}. Enjoy your meal! I\'ll send to {}.'.format(cusinie_type, num_people, date, dinning_time, api_res, email)}
                )"""
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'You’re all set. Expect my recommendations shortly! Have a good day.'
                  }
                )


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']
    print (intent_name)

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Hi there, how can I help?'})
    if intent_name == 'ThankYouIntent':
        return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'You\'re welcome. Have a nice day!'})
    if intent_name == 'DiningSuggestionsIntent':
        return dinning_suggest(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
