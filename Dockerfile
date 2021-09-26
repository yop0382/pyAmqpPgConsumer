FROM debian:stable-slim
RUN apt update && apt install python3 python3-pip -y
RUN pip3 install pika psycopg2-binary
COPY ./ ./
ENTRYPOINT ["python3", "main.py"]