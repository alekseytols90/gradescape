from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from mygrades.models import Assignment


class Command(BaseCommand):
    def handle(self, *args, **options):
        assignments = Assignment.objects.filter(status="Assigned", active=True)

        for assignment in assignments:
            if assignment.submission_date < timezone.now():
                assignment.late = True
                assignment.active = False
                assignment.save()
            else:
                pass
        self.stdout.write(self.style.SUCCESS("Assignment status has been updated"))
