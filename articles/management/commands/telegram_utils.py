from django.core.management.base import BaseCommand
from articles.telegram_bot import main


class Command(BaseCommand):
    help = "Run the Telegram bot"

    def handle(self, *args, **options):
        main()
