#!/usr/bin/env python

from datetime import datetime
import docker
from prometheus_client import start_http_server, Gauge
import os
import platform
import traceback
import signal
from time import sleep
from typing import Any

def handle_shutdown(signal: Any, frame: Any) -> None:
    print_timed(f"Received signal {signal}. Shutting down...")
    exit(0)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

APP_NAME = "Docker services Prometheus exporter"
INSTANCES_METRIC = Gauge('docker_service_instances',
                         'Number of desired replicas for a service',
                         ['service_id', 'service_name', 'image', 'docker_hostname'])
RUNNING_TASKS_METRIC = Gauge('docker_service_running_tasks',
                             'Number of running tasks for a service',
                             ['service_id', 'service_name', 'image', 'docker_hostname'])

PROMETHEUS_EXPORT_PORT = int(os.getenv('PROMETHEUS_EXPORT_PORT', '9000'))
DOCKER_HOSTNAME = os.getenv('DOCKER_HOSTNAME', platform.node())
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '30'))  # Default to 30s polling interval

def print_timed(msg):
    to_print = '{} [{}]: {}'.format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'docker_services',
        msg)
    print(to_print)

def collect_services():
    client = docker.DockerClient()
    try:
        services = client.services.list()
        INSTANCES_METRIC.clear()
        RUNNING_TASKS_METRIC.clear()

        for service in services:
            details = service.attrs
            service_id = details.get('ID', '')
            spec = details.get('Spec', {})
            service_name = spec.get('Name', 'unknown')
            image = spec.get('TaskTemplate', {}).get('ContainerSpec', {}).get('Image', 'unknown')
            mode = details.get('Spec', {}).get('Mode', {})
            replicas = mode.get('Replicated', {}).get('Replicas', 0) if 'Replicated' in mode else 1

            tasks = service.tasks(filters={'service': service_id})
            running_tasks = sum(1 for task in tasks if task.get('Status', {}).get('State') == 'running')

            INSTANCES_METRIC.labels(
                service_id=service_id,
                service_name=service_name,
                image=image,
                docker_hostname=DOCKER_HOSTNAME
            ).set(replicas)

            RUNNING_TASKS_METRIC.labels(
                service_id=service_id,
                service_name=service_name,
                image=image,
                docker_hostname=DOCKER_HOSTNAME
            ).set(running_tasks)
    finally:
        client.close()

if __name__ == '__main__':
    print_timed(f'Start Prometheus client on port {PROMETHEUS_EXPORT_PORT}')
    start_http_server(PROMETHEUS_EXPORT_PORT, addr='0.0.0.0')
    while True:
        try:
            print_timed('Collecting Docker service information...')
            collect_services()
        except docker.errors.APIError:
            traceback.print_exc()
            print_timed("Docker API error. Retrying...")
        sleep(POLL_INTERVAL)
