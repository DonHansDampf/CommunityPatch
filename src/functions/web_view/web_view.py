import logging
from operator import itemgetter
import os

import boto3
import jinja2

function_dir = os.path.dirname(os.path.abspath(__file__))

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(function_dir, 'templates')),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

template = jinja2_env.get_template('index.html')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb').Table(os.getenv('DEFINITIONS_TABLE'))


def scan_table():
    results = dynamodb.scan()
    while True:
        for row in results['Items']:
            yield row
        if results.get('LastEvaluatedKey'):
            results = dynamodb.scan(
                ExclusiveStartKey=results['LastEvaluatedKey'])
        else:
            break


def get_titles():
    title_list = list()

    for item in scan_table():
        title = dict()
        title['is_synced'] = item.get('is_synced')
        title['last_sync_result'] = item.get('last_sync_result')
        title.update(item['title_summary'])
        title_list.append(title)

    return sorted(title_list, key=itemgetter('name'))


def lambda_handler(event, context):
    return template.render(titles=get_titles())
