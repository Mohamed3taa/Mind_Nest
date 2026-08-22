from django.core.management.base import BaseCommand
from planner.models import Task


class Command(BaseCommand):
    help = 'Sync is_completed field with task status'

    def handle(self, *args, **kwargs):
        done   = Task.objects.filter(status='done', is_completed=False).update(is_completed=True)
        undone = Task.objects.filter(status__in=['todo', 'in_progress'], is_completed=True).update(is_completed=False)
        self.stdout.write(self.style.SUCCESS(
            f'Synced: {done} set completed, {undone} set incomplete'
        ))
