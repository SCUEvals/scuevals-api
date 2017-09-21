import requests
import argparse


SCU_URL = 'https://www.scu.edu/apps/ws/courseavail/'


def main():
    parser = argparse.ArgumentParser(description='Scrape the SCU CourseAvail API.')
    parser.add_argument('--api', '-a', dest='api', required=True, help='Where to post the scraped data.')
    parser.add_argument('type', choices=['departments', 'courses'], help='What to scrape.')

    args = parser.parse_args()

    if args.type == 'departments':
        data = departments()
    elif args.type == 'courses':
        data = courses()
    else:
        return

    post(args.api, data)


def departments():
    resp = requests.get(SCU_URL + 'autocomplete/departments')
    if not resp.status_code == 200:
        raise Exception('Non-OK status code: ' + str(resp.status_code))

    deps = {'departments': resp.json()['results']}

    return deps


def courses():
    pass


def post(api, data):
    data['university_id'] = 1

    resp = requests.post(api, json=data)
    if not resp.status_code == 200:
        raise Exception('Non-OK status code: ' + str(resp.status_code))

    json = resp.json()

    if 'error' in json:
        raise Exception('Error: ' + json['error'])

    print('Updated {} records.'.format(json['updated_count']))


main()
