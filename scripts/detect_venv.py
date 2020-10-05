from utils import in_virtualenv


def main():
    in_venv = in_virtualenv()
    print(in_venv)


if __name__ == "__main__":
    main()
