import json
from django.core.management.base import BaseCommand
from courses.models import Course

class Command(BaseCommand):
    help = 'Seeds the database with initial course data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting existing course data...")
        Course.objects.all().delete()
        
        self.stdout.write("Creating new course data...")

        courses_data = [
            {
                "title": "Pengenalan Investasi untuk Pemula",
                "description": "Pelajari dasar-dasar investasi saham, reksadana, dan obligasi.",
                "instructor": "Gro Investor",
                "topics": json.dumps(["Saham", "Reksadana", "Obligasi"]),
                "price": 50.00
            },
            {
                "title": "Strategi Marketing Digital 2025",
                "description": "Kuasai SEO, SEM, dan media sosial untuk meningkatkan bisnis Anda.",
                "instructor": "Luiy Marketer",
                "topics": json.dumps(["SEO", "Social Media", "Content Marketing"]),
                "price": 75.50
            },
            {
                "title": "Dasar-Dasar Memasak Gelato",
                "description": "Kursus wajib untuk Toto dan semua Nimon yang suka gelato.",
                "instructor": "Chef Toto",
                "topics": json.dumps(["Bahan Dasar", "Teknik Pembekuan", "Penyajian"]),
                "price": 40.00
            },
            {
                "title": "Seni Bermain Gitar (Anti Fals)",
                "description": "Dari kunci dasar hingga melodi indah, dijamin tetangga tidak akan pindah.",
                "instructor": "Stewart Musician",
                "topics": json.dumps(["Kunci Dasar", "Strumming", "Teori Musik"]),
                "price": 60.00
            },
            {
                "title": "Mitologi Makhluk Fantasi",
                "description": "Jelajahi dunia unicorn, naga, dan makhluk mitos lainnya bersama Pop.",
                "instructor": "Pop the Storyteller",
                "topics": json.dumps(["Unicorn", "Naga", "Griffin"]),
                "price": 35.00
            }
        ]

        for data in courses_data:
            Course.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with courses.'))