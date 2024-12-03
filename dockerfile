FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime as base
WORKDIR /app
COPY . .
EXPOSE 8000
RUN pip install -r requirements.txt
WORKDIR /app/api/
ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
