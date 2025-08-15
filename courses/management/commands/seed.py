from django.core.management.base import BaseCommand
from courses.models import Course, Module

class Command(BaseCommand):
    help = "Seed initial data"

    def handle(self, *args, **kwargs):
        if Course.objects.exists():
            self.stdout.write(self.style.WARNING("Already seeded")); return
        c = Course.objects.create(title="Go Fundamentals", description="Belajar dasar Go", price=199000)
        Module.objects.create(course=c, title="Intro", content="Welcome", order=1)
        Module.objects.create(course=c, title="Variables", content="Let’s go", order=2)
        self.stdout.write(self.style.SUCCESS("Seeded"))
