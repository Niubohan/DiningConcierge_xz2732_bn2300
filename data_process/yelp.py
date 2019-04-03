import requests
import time
from collections import defaultdict
import boto3

API_Key = ""
cusinies = ['japanese', 'chinese', 'american', 'italian', 'mexican', 'korean', 'thai', 'russian', 'spanish', 'vietnamese']
full_dic, id_list = defaultdict(list), []
client = boto3.resource('dynamodb')
table = client.Table('yelp-restaurants')


def yelp_search(cusinie):
    headers = {
        'Authorization': 'Bearer %s' % API_Key,
    }
    offset, length = 0, 1000
    while offset < min(1000, length):
        url = "https://api.yelp.com/v3/businesses/search?location={}&categories={}&offset={}".format('Manhattan', cusinie, offset)
        api_response = requests.request('GET', url, headers=headers).json()
        length = api_response['total']
        for restaurant in api_response['businesses']:
            if restaurant['id'] not in id_list:
                item = {
                    'Business ID' : restaurant['id'],
                    'Name' : restaurant['name'],
                    'Address' : restaurant['location']['address1'] if restaurant['location']['address1'] else None,
                    'Coordinates' : ",".join([str(restaurant['coordinates']['latitude']), str(restaurant['coordinates']['longitude'])]),
                    'Number of Reviews' : str(restaurant['review_count']),
                    'Rating' : str(restaurant['rating']),
                    'Zip Code' : str(restaurant['location']['zip_code']) if restaurant['location']['zip_code'] else None,
                    'insertedAtTimestamp' : str(int(time.time()))
                }
                try:
                    table.put_item(Item=item)
                except:
                    print(item)
                full_dic[cusinie].append((restaurant['id'], str(restaurant['rating']), str(restaurant['review_count'])))
                id_list.append(restaurant['id'])
        offset += 20
        print('get {} item {} offset {}'.format(cusinie, str(len(full_dic[cusinie])), str(offset)))


for cusinie in cusinies:
    yelp_search(cusinie)

test_file = open('data/full.csv', 'w', encoding='utf-8')

for cusinie in full_dic:
    for item in full_dic[cusinie]:
        test_file.writelines("{}, {}, {}, {}\n".format(item[0], cusinie, item[1], item[2]))




