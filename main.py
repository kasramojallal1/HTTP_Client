import requests
import sys
import re
from colorama import Fore, Style
from tqdm import tqdm
import socket


def handle_data():
    url = get_url()
    method = 'GET'
    headers_dic = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    query_dic = {}
    data = ''
    content_type_set = 0
    timeout = None
    file_address = None


    for i in range(len(sys.argv)):
        if i == 0:
            continue
        if sys.argv[i] == '-M' or sys.argv[i] == '--method':
            try:
                method = get_method(sys.argv[i + 1])
            except IndexError:
                print(Fore.RED + 'Please write the method')
                exit()

        if sys.argv[i] == '-H' or sys.argv[i] == '--headers':
            try:
                content_type_set = get_headers(sys.argv[i + 1], headers_dic, content_type_set)
            except IndexError:
                print(Fore.RED + 'Please write the headers')
                exit()

        if sys.argv[i] == '-Q' or sys.argv[i] == '--queries':
            try:
                get_queries(sys.argv[i + 1], query_dic)
            except IndexError:
                print(Fore.RED + 'Please write the queries')
                exit()

        if sys.argv[i] == '-D' or sys.argv[i] == '--data':
            try:
                data = get_data(sys.argv[i + 1], headers_dic)
            except IndexError:
                print(Fore.RED + 'Please write the data')
                exit()

        if sys.argv[i] == '--json':
            if not content_type_set:
                headers_dic['content-type'] = 'application/json'
            try:
                data = get_json(sys.argv[i + 1], headers_dic)
            except IndexError:
                print(Fore.RED + 'Please write the data')
                exit()

        if sys.argv[i] == '--timeout':
            try:
                timeout = int(sys.argv[i + 1])
            except IndexError:
                print(Fore.RED + 'Please write the timeout')
                exit()

        if sys.argv[i] == '--file':
            if not content_type_set:
                headers_dic['content-type'] = 'application/octet-stream'
            try:
                file_address = sys.argv[i + 1]
            except IndexError:
                print(Fore.RED + 'Please write the file address')
                exit()




    handle_request(url, method, headers_dic, query_dic, data, timeout, file_address)


def handle_request(url, method, headers_dic, query_dic, data, timeout, file_address):\

    files = None
    if file_address:
        try:
            files = {'file': open(file_address, 'rb')}
        except FileNotFoundError:
            print(Fore.RED + 'file not found!' + Style.RESET_ALL)
            exit()

    if method == 'GET':
        try:
            req_response = None
            req_response = requests.get(url=url, headers=headers_dic, params=query_dic,
                                        timeout=timeout, files=files, stream=True)
            total_size_in_bytes = int(req_response.headers.get('content-length', 0))
            block_size = 1024
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open('test.dat', 'wb') as file:
                for data in req_response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()

            http_version = get_http_version(str(req_response.raw.version))
            print('HTTP/' + str(http_version) + ' ' + str(req_response.status_code) + ' ' + str(req_response.reason))
            handle_response_headers(req_response.headers)
            req_response = requests.get(url=url, headers=headers_dic, params=query_dic,
                                        timeout=timeout, files=files, stream=True)
            print(req_response.text)
        except (requests.exceptions.RequestException, ValueError) as e:
            print(Fore.RED + 'Timeout error')


    if method == 'POST':
        try:
            req_response = None
            req_response = requests.post(url=url, headers=headers_dic, params=query_dic,
                                        data=data, timeout=timeout, files=files)
            req_response.raise_for_status()
            http_version = get_http_version(str(req_response.raw.version))
            print('HTTP/' + str(http_version) + ' ' + str(req_response.status_code) + ' ' + str(req_response.reason))
            handle_response_headers(req_response.headers)
            print(req_response.text)
        except (requests.exceptions.RequestException, ValueError) as e:
            print(Fore.RED + 'Timeout error')

    if method == 'PUT':
        req_response = requests.put(url=url, headers=headers_dic, params=query_dic,
                                    data=data, timeout=timeout, files=files)
        http_version = get_http_version(str(req_response.raw.version))
        print('HTTP/' + str(http_version) + ' ' + str(req_response.status_code) + ' ' + str(req_response.reason))
        handle_response_headers(req_response.headers)
        print(req_response.text)

    if method == 'DELETE':
        req_response = requests.delete(url=url, headers=headers_dic, params=query_dic,
                                       data=data, timeout=timeout, files=files)
        http_version = get_http_version(str(req_response.raw.version))
        print('HTTP/' + str(http_version) + ' ' + str(req_response.status_code) + ' ' + str(req_response.reason))
        handle_response_headers(req_response.headers)
        print(req_response.text)

    if method == 'PATCH':
        req_response = requests.patch(url=url, headers=headers_dic, params=query_dic,
                                      data=data, timeout=timeout, files=files)
        http_version = get_http_version(str(req_response.raw.version))
        print('HTTP/' + str(http_version) + ' ' + str(req_response.status_code) + ' ' + str(req_response.reason))
        handle_response_headers(req_response.headers)
        print(req_response.text)


def get_http_version(http_version):
    if http_version == '11':
        http_version = '1.1'
    elif http_version == '9':
        http_version = '0.9'
    elif http_version == '10':
        http_version = '1.0'
    elif http_version == '20':
        http_version = '2.0'

    return http_version


def handle_response_headers(response_headers_dic):
    for key in response_headers_dic:
        print(Fore.CYAN + str(key) + ': ' + Style.RESET_ALL + str(response_headers_dic[key]))


def get_json(string, headers_dic):

    if headers_dic['content-type'] == 'application/json':
        if not re.search('^{"(.)+":(\s)*"(.)*"(,(\s)*"(.)+":(\s)*"(.)*")*}', string):
            print(Fore.YELLOW + 'your content type does not match your input data' + Style.RESET_ALL)

    return string


def get_data(string, headers_dic):

    if headers_dic['content-type'] == 'application/x-www-form-urlencoded':
        pairs = string.split('&')
        for pair_values in pairs:
            try:
                key, value = pair_values.split('=')
            except ValueError:
                print(Fore.YELLOW + 'your content type does not match your input data' + Style.RESET_ALL)

    return string


def get_queries(string, query_dic):
    string = string.lower()
    pairs = string.split('&')

    for pair_value in pairs:
        new_pair = pair_value.split('=')

        if new_pair[0] in query_dic:
            query_dic[new_pair[0]] = new_pair[1]
            print(Fore.YELLOW + str(new_pair[0]) + ' query, was replaced' + Style.RESET_ALL)
        else:
            query_dic[new_pair[0]] = new_pair[1]


def get_headers(string, headers_dic, content_type_set):
    string = string.lower()
    pairs = string.split(',')

    for pair_value in pairs:
        new_pair = pair_value.split(':')

        if new_pair[0] == 'content-type':
            content_type_set = 1
            headers_dic['content-type'] = new_pair[1]

        if new_pair[0] in headers_dic:
            headers_dic[new_pair[0]] = new_pair[1]
            print(Fore.YELLOW + str(new_pair[0]) + ' header, was replaced' + Style.RESET_ALL)
        else:
            headers_dic[new_pair[0]] = new_pair[1]

    return content_type_set


def get_method(string):
    available_methods = ['get', 'post', 'put', 'patch', 'delete']

    string = string.lower()
    if string in available_methods:
        return string.upper()
    else:
        print(Fore.RED + 'Error: Method ' + string + ' is not recognized. '
                                                     'Use GET, POST, PUT, PATCH and DELETE instead.')
        exit()


def get_url():
    try:
        url = sys.argv[1]
        validity = is_valid_url(url)
        if not validity:
            print(Fore.RED + 'Error: Malformed URL')
            exit()
        return url
    except IndexError:
        print(Fore.RED + 'url is not set')
        exit()


def is_valid_url(string):
    regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=-]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

    p = re.compile(regex)

    if string is None:
        return False

    if re.search(p, string):
        return True
    else:
        return False


if __name__ == "__main__":
    handle_data()
