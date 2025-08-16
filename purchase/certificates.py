from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from io import BytesIO

class CertificateGenerator:
    """
    Kelas untuk menghasilkan PDF Certificate of Completion.
    Method .generate() bersifat statis sehingga mudah dipanggil dari views.
    """
    @staticmethod
    def generate(username, course_title, instructor, completed_date):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        w, h = A4

        # Judul sertifikat
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(w/2, h-150, "Certificate of Completion")

        # Nama penerima
        c.setFont("Helvetica", 16)
        c.drawCentredString(w/2, h-220, "This certifies that")
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(w/2, h-250, username)

        # Informasi course
        c.setFont("Helvetica", 16)
        c.drawCentredString(w/2, h-290, "has successfully completed the course")
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(w/2, h-320, f"\"{course_title}\"")

        # Instructor & tanggal
        c.setFont("Helvetica", 14)
        c.drawCentredString(w/2, h-360, f"Instructor: {instructor}")
        c.drawCentredString(w/2, h-390, f"Date: {completed_date.strftime('%B %d, %Y')}")

        c.showPage()
        c.save()

        pdf = buffer.getvalue()
        buffer.close()

        filename = f"certificate_{username}_{course_title}.pdf".replace(" ", "_")
        return ContentFile(pdf, name=filename)