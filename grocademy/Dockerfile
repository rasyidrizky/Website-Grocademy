# Dockerfile

# Menggunakan versi Python yang sudah kita verifikasi sebelumnya
ARG PYTHON_VERSION=3.11-slim-buster
FROM python:${PYTHON_VERSION}

# Mengatur environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Mengatur working directory ke /app
WORKDIR /app

# Menginstal dependensi sistem yang dibutuhkan oleh psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Menyalin file requirements terlebih dahulu untuk caching
COPY requirements.txt .

# Menginstal dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode proyek ke dalam working directory
COPY . .

# Menjalankan collectstatic untuk mengumpulkan semua file statis
RUN python manage.py collectstatic --noinput

# Memberi tahu Docker bahwa aplikasi berjalan di port 8000
EXPOSE 8000

# Perintah untuk menjalankan aplikasi menggunakan Gunicorn
CMD ["gunicorn", "monolith.wsgi:application", "--bind", "0.0.0.0:8000"]