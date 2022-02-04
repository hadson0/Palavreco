from bot import Bot
from setup import get_client


def main():
    client = get_client()
    bot = Bot(client)

    while True:
        bot.search_mentions()


if __name__ == "__main__":
    main()
