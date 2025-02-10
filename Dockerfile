FROM python:3.10-alpine

ADD src /opt/docker-service-exporter
WORKDIR /opt/docker-service-exporter

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "./service_notifier.py"]