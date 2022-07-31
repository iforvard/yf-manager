from flet import flet

from yf_manager import YFManagerApp


def main():
    flet.app(target=YFManagerApp, port=9000)


if __name__ == "__main__":
    main()
