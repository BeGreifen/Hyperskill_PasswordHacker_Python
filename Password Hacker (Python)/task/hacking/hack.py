import argparse
import socket
import itertools
import string
import logging
import inspect
import requests
import os


# write your code here
def logger(func):
    def wrap(*args, **kwargs):
        logging.info(
            f"{func.__name__} - line no: {inspect.getframeinfo(inspect.currentframe().f_back).lineno} with args: {args}, kwargs: {kwargs}")
        # Log the function name and arguments

        # Call the original function
        result = func(*args, **kwargs)

        # Log the return value
        logging.info(f"{func.__name__} returned: {result}")

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
    char_list = string.ascii_lowercase + string.digits
    for i in range(1, length + 1):
        for combo in itertools.product(char_list, repeat=i):
            yield ''.join(combo)


@logger
def get_typical_passwords_file():
    url = "https://stepik.org/media/attachments/lesson/255258/passwords.txt"
    filename = url.split("/")[-1]  # Extract the filename from the URL

    response = requests.get(url)

    if response.status_code == 200:
        current_working_dir = os.getcwd()
        logging.info(current_working_dir)
        with open(filename, "wb") as file:
            file.write(response.content)
            return "\\".join([current_working_dir, file.name])
    else:
        print("Failed to download the file.")


# @logger
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
        # logging.info([pw, message, response])
        return response
    elif response == "Too many attempts":
        # logging.info([pw, message, response])
        return response


@logger
def get_dict_pass(hostname, port):
    dict_file = get_typical_passwords_file()
    with socket.socket() as client_socket:
        address = (hostname, port)
        client_socket.connect(address)
        with open(dict_file, "r") as file:
            for line in file:
                # logging.info(["line:", line[:-1], isinstance(line[:-1], int)])
                try:
                    ans = test_password(client_socket, int(line[:-1]))
                    # logging.info(["ans:", ans])
                    if ans != "Wrong password!":
                        # logging.info(["ans:", ans])
                        return ans
                except:
                    char_combinations = [
                        [letter.lower(), letter.upper()] if isinstance(letter, str) else [letter]
                        for letter in line[:-1]]
                    password_list = [''.join(x) for x in itertools.product(*char_combinations)]
                    # logging.info(["password list:", password_list])
                    for password in password_list:
                        # logging.info(password)
                        ans = test_password(client_socket, password)
                        # logging.info(["ans:", ans])
                        if ans != "Wrong password!":
                            logging.info(["ans:", ans])
                            return ans


@logger
def send_message_and_get_response(hostname: str, port: int, message: str = "") -> socket:
    with socket.socket() as client_socket:
        address = (hostname, port)
        client_socket.connect(address)
        for password in get_brute_force_pass():
            message = password.encode()
            client_socket.send(message)
            response = client_socket.recv(1024)
            response = response.decode()
            if response in "Connection success!":
                logging.info(["password:", password, "message:", message, "response:", response])
                return password
            elif response in "Too many attempts":
                logging.info([password, message, response])
                return response


@logger
def main():
    args = get_args()
    # ans = send_message_and_get_response(args.ip_address,
    #                                     args.port)
    ans = get_dict_pass(args.ip_address, args.port)
    print(ans)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='app.log',  # Specify the file name for logging
                        filemode='w'  # Use 'w' mode to overwrite the log file on each run, or 'a' to append
                        )
    main()
