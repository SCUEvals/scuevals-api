import os
import requests
import argparse
import re
from bs4 import BeautifulSoup

SCU_URL = 'https://www.scu.edu/'
SCU_API_URL = SCU_URL + 'apps/ws/courseavail/'


def main():
    parser = argparse.ArgumentParser(description='Scrape the SCU CourseAvail API.')
    parser.add_argument('--api', '-a', dest='api', required=True, help='Where to post the scraped data.')

    subparsers = parser.add_subparsers(help='What to scrape.')

    courses_parser = subparsers.add_parser('courses')
    courses_parser.add_argument('--quarter-id', '-q', dest='quarter_id', required=True, help='Which quarter to scrape.')
    courses_parser.set_defaults(func=scrape_courses)

    deps_parser = subparsers.add_parser('departments')
    deps_parser.set_defaults(func=scrape_departments)

    majors_parser = subparsers.add_parser('majors')
    majors_parser.set_defaults(func=scrape_majors)

    args = parser.parse_args()

    args.func(args)


def scrape_departments(args):
    resp = requests.get(SCU_API_URL + 'autocomplete/departments')
    if not resp.status_code == 200:
        raise Exception('Non-OK status code: ' + str(resp.status_code))

    deps = {'departments': resp.json()['results']}

    post(args.api, '/departments', deps)


def scrape_courses(args):
    deps = get(args.api, '/departments')

    for dep in deps:
        params = {'dept': dep['abbr'], 'school': dep['school']}
        resp = requests.post(SCU_API_URL + 'search/{}/ugrad'.format(args.quarter_id), data=params)
        if not resp.status_code == 200:
            raise Exception('Non-OK status code: ' + str(resp.status_code))

        courses = {'courses': resp.json()['results']}
        post(args.api, '/courses', courses)


def scrape_majors(args):
    resp = requests.get(SCU_URL + 'academics/undergraduate-programs/')
    if not resp.status_code == 200:
        raise Exception('Non-OK status code: ' + str(resp.status_code))

    soup = BeautifulSoup(resp.text, 'html.parser')
    elements = soup.select_one('.intro').parent.select('li a')

    exclusions = ['Modern Languages and Literatures']
    all_majors = []

    regex = re.compile(r'\(.+\)')

    for element in elements:
        major = element.string
        if major is None or major in exclusions:
            continue

        major = regex.sub('', major).strip()

        if major in all_majors:
            continue

        print(major)
        all_majors.append(major)

    confirm = input('\nDo you want to submit these majors to the API? (Y/n): ')

    if confirm != 'Y':
        return

    majors = {'majors': all_majors}
    post(args.api, '/majors', majors)


def get(api, path):
    jwt = authenticate(api)
    resp = requests.get(api + path, params={'university_id': 1}, headers={'Authorization': 'Bearer ' + jwt})
    if not resp.status_code == 200:
        raise Exception('Non-OK status code: ' + str(resp.status_code))

    data = resp.json()

    if 'error' in data:
        raise Exception('Error: ' + data['error'])

    return data


def authenticate(api):
    api_key = os.environ['API_KEY']
    resp = requests.post(api + '/auth/api',
                         headers={'Content-Type': 'application/json'},
                         json={'api_key': api_key})
    data = resp.json()

    if 'jwt' not in data:
        print(data)
        raise Exception('Error: failed to authenticate')

    return data['jwt']


def post(api, path, data):
    data['university_id'] = 1

    jwt = authenticate(api)

    resp = requests.post(api + path, json=data, headers={'Authorization': 'Bearer ' + jwt})

    if not resp.status_code == 200:
        data = resp.json()
        print(data)
        raise Exception('Non-OK status code: ' + str(resp.status_code))

    data = resp.json()

    if 'error' in data:
        raise Exception('Error: ' + data['error'])

    if 'updated_count' in data:
        print('Updated {} records.'.format(data['updated_count']))
    else:
        print('Success')


main()
