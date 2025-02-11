# Docker Service Exporter

## Description
Docker Service Exporter is a Prometheus exporter that monitors Docker Swarm services and provides metrics for desired instances and running tasks. It allows users to track discrepancies between expected and actual service states, helping ensure service reliability.

## Build Instructions
To build the Docker image for the exporter, follow these steps:

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Build the Docker image:
   ```sh
   docker build -t docker-service-exporter .
   ```
3. Run the container:
   ```sh
   docker run -d -p 9000:9000 --name service-exporter docker-service-exporter
   ```

## Prometheus Alert Rule Example
To trigger an alert when the number of running tasks for `nginx` is below the number of desired instances, use the following Prometheus alert rule configuration:

```yaml
groups:
  - name: docker_service_alerts
    rules:
      - alert: NginxRunningTasksBelowInstances
        expr: docker_service_running_tasks{service_name="nginx"} < docker_service_instances{service_name="nginx"}
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Nginx running tasks below instances"
          description: "The number of running tasks for the nginx service is lower than the desired instances."
```

