from framework.util.db import get_db_name


def main():
    name = get_db_name()
    print(name)


if __name__ == "__main__":
    main()
