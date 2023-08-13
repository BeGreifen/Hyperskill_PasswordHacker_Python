import argparse
import socket


# write your code here


def set_args():
    parser = argparse.ArgumentParser(description="Commandline inputs to start Hacking Password script.")
    parser.add_argument("ip_address", type=str,
                        help="like localhost or 127.0.0.1")
    parser.add_argument("port", type=int,
                        help="like 8080")
    parser.add_argument("message", type=str,
                        help="string that you want to send, like this is a test")
    return parser


def get_args() -> argparse:
    parser = set_args()
    parser.parse_args()
    return parser


def send_message_and_get_response(hostname: str, port: int, message: str) -> socket:
    with socket.socket() as client_socket:
        address = (hostname, port)
        client_socket.connect(address)

        message = message.encode()
        client_socket.send(message)

        response = client_socket.recv(port)
        response = response.decode()
        return response


def main():
    parser = get_args()
    args = parser.parse_args()
    ans = send_message_and_get_response(args.ip_address,
                                        args.port,
                                        args.message)
    print(ans)


if __name__ == "__main__":
    main()
