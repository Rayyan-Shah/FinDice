from django.core.management.base import BaseCommand
from core.emails import send_monthly_summaries

class Command(BaseCommand):
    help = 'Send monthly financial summary emails to all users.'

    def handle(self, *args, **kwargs):
        send_monthly_summaries()
        self.stdout.write(self.style.SUCCESS('Successfully sent all monthly financial summaries.'))
