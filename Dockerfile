ARG ALPINE_VER=3.16
ARG TERRAFORM_VER=1.3.2
ARG PYTHON_VER=3.10.5

# terraform
FROM hashicorp/terraform:${TERRAFORM_VER} as terraform
LABEL maintainer="Jalal Hosseini - @artronics"

# aws cli
FROM python:${PYTHON_VER}-alpine${ALPINE_VER} as awscli

ARG AWS_CLI_VER=2.7.24
RUN apk add --no-cache git unzip groff build-base libffi-dev cmake
RUN git clone --single-branch --depth 1 -b ${AWS_CLI_VER} https://github.com/aws/aws-cli.git

WORKDIR aws-cli
RUN sed -i'' 's/PyInstaller.*/PyInstaller==5.2/g' requirements-build.txt
RUN python -m venv venv
RUN . venv/bin/activate
RUN scripts/installers/make-exe
RUN unzip -q dist/awscli-exe.zip
RUN aws/install --bin-dir /aws-cli-bin
RUN /aws-cli-bin/aws --version

# reduce image size: remove autocomplete and examples
RUN rm -rf /usr/local/aws-cli/v2/current/dist/aws_completer /usr/local/aws-cli/v2/current/dist/awscli/data/ac.index /usr/local/aws-cli/v2/current/dist/awscli/examples
RUN find /usr/local/aws-cli/v2/current/dist/awscli/botocore/data -name examples-1.json -delete

# final image
FROM python:${PYTHON_VER}-alpine${ALPINE_VER}

RUN apk add --update make docker openrc
RUN rc-update add docker boot

COPY --from=awscli /usr/local/aws-cli/ /usr/local/aws-cli/
COPY --from=awscli /aws-cli-bin/ /usr/local/bin/

COPY --from=terraform /bin/terraform /bin/terraform

COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
