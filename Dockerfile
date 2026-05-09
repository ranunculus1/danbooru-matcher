FROM python:3.11-slim

WORKDIR /app

RUN pip3 install flask --no-cache-dir

COPY . .

EXPOSE 7860

ENV HF_SPACE_ID=true

CMD ["python3", "app.py", "--port", "7860", "--host", "0.0.0.0"]
