FROM hashicorp/terraform:1.3.2 as terraform
LABEL maintainer="Jalal Hosseini - @artronics"

FROM python:3.9.14-alpine3.16

RUN apk add --update make docker openrc
RUN rc-update add docker boot

COPY --from=terraform /bin/terraform /bin/terraform

COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
