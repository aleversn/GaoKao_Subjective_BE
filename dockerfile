FROM ubuntu/nginx:1.26-24.10_edge as base
WORKDIR /app
COPY . .
EXPOSE 8000
RUN pip install -r requirements.txt
WORKDIR /app/api/
ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
