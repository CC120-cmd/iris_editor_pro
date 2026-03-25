FROM python:3.10-slim

WORKDIR /app

# 🔥 ADD THIS LINE (important)
RUN apt-get update && apt-get install -y build-essential

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]