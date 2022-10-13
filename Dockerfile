FROM hashicorp/terraform:1.3.2 as terraform
LABEL maintainer="Jalal Hosseini - @artronics"

FROM python:3.9.14-alpine3.16
COPY --from=terraform /bin/terraform /bin/terraform

COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]

