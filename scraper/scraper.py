import requests
import argparse

SCU_URL = 'https://www.scu.edu/apps/ws/courseavail/'


def main():
    parser = argparse.ArgumentParser(description='Scrape the SCU CourseAvail API.')
    parser.add_argument('--api', '-a', dest='api', required=True, help='Where to post the scraped data.')

    subparsers = parser.add_subparsers(help='What to scrape.')

    courses_parser = subparsers.add_parser('courses')
    courses_parser.add_argument('--quarter-id', '-q', dest='quarter_id', required=True, help='Which quarter to scrape.')
    courses_parser.set_defaults(func=scrape_courses)

    deps_parser = subparsers.add_parser('departments')
    deps_parser.set_defaults(func=scrape_departments)

    args = parser.parse_args()

    args.func(args)


def scrape_departments(args):
    resp = requests.get(SCU_URL + 'autocomplete/departments')
    if not resp.status_code == 200:
        raise Exception('Non-OK status code: ' + str(resp.status_code))

    deps = {'departments': resp.json()['results']}

    post(args.api + '/departments', deps)


def scrape_courses(args):
    deps = get(args.api + '/departments')

    for dep in deps:
        params = {'dept': dep['abbr'], 'school': dep['school']}
        resp = requests.post(SCU_URL + 'search/{}/ugrad'.format(args.quarter_id), data=params)
        if not resp.status_code == 200:
            raise Exception('Non-OK status code: ' + str(resp.status_code))

        courses = {'courses': resp.json()['results']}
        post(args.api + '/courses', courses)


def get(api):
    resp = requests.get(api, params={'university_id': 1})
    if not resp.status_code == 200:
        raise Exception('Non-OK status code: ' + str(resp.status_code))

    json = resp.json()

    if 'error' in json:
        raise Exception('Error: ' + json['error'])

    return json


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
