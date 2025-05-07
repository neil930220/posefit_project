from django.core.management.base import BaseCommand
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Delete expired outstanding and blacklisted tokens'

    def handle(self, *args, **kwargs):
        # Delete expired outstanding tokens
        expired_tokens = OutstandingToken.objects.filter(expires_at__lt=now())
        count = expired_tokens.count()
        expired_tokens.delete()
        self.stdout.write(f"Deleted {count} expired outstanding tokens.")

        # Optionally: delete orphaned blacklisted tokens if needed
