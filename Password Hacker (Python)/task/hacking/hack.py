import argparse
import socket
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
    parser.add_argument("message", type=str,
                        help="string that you want to send, like this is a test")
    return parser


@logger
def get_args() -> argparse:
    parser = set_args()
    parser.parse_args()
    return parser


@logger
def send_message_and_get_response(hostname: str, port: int, message: str) -> socket:
    with socket.socket() as client_socket:
        address = (hostname, port)
        client_socket.connect(address)

        message = message.encode()
        client_socket.send(message)

        response = client_socket.recv(port)
        response = response.decode()
        return response


@logger
def main():
    parser = get_args()
    args = parser.parse_args()
    ans = send_message_and_get_response(args.ip_address,
                                        args.port,
                                        args.message)
    print(ans)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='app.log',  # Specify the file name for logging
                        filemode='w'  # Use 'w' mode to overwrite the log file on each run, or 'a' to append
                        )
    main()
