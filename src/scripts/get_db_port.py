from framework.util.db import get_db_port


def main():
    port = get_db_port()
    print(port)


if __name__ == "__main__":
    main()
