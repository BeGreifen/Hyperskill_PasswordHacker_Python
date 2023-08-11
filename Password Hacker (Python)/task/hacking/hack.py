import argparse
# write your code here


def set_args():
    parser = argparse.ArgumentParser(description="Getting commandline inputs to start Hacking Password script.")
    parser.add_argument("ip_address", type=str)
    parser.add_argument("port", type=int)
    parser.add_argument("message", type=str)
    return parser


def get_args() -> argparse:
    parser = set_args()
    parser.parse_args()
    return parser


def main():
    parser = get_args()
    print(parser.parse_args())

if __name__ == "__main__":
    main()