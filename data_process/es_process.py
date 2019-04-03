import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

test_file = [line.strip().split(', ') for line in open('data/test.csv', 'r').readlines()]
test_res = [json.loads(item.strip()) for item in open('data/predict.csv.out', 'r').readlines()]

host = 'search-hw2-mczdnqn2de2rh43xufhc6yfgwa.us-east-1.es.amazonaws.com'
region = 'us-east-1'
bulk_file = ''

service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service)

es = Elasticsearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)

for i in range(len(test_file)):
    if test_res[i]['predicted_label']:
        index = {
            'index': {
                '_index': 'predictions',
                '_type': 'Prediction',
                '_id': test_file[i][0]
            }
        }
        bulk_file += json.dumps(index) + "\n"
        fields = {
                'RestaurantId': test_file[i][0],
                'Cuisine': test_file[i][1],
                'Score': test_res[i]['score']
        }
        bulk_file += json.dumps(fields) + "\n"

es.bulk(bulk_file)