FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/app/data

EXPOSE 8786

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8786"]