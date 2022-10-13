FROM hashicorp/terraform:1.3.2 as terraform
LABEL maintainer="Jalal Hosseini - @artronics"

FROM alpine:3.16.2
COPY --from=terraform /bin/terraform /bin/terraform

RUN apk add --update bash

CMD ["/bin/bash", "-c"]
