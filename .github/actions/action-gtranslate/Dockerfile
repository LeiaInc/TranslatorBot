FROM alpine:3.10

LABEL "com.github.actions.name"="Strings translater"
LABEL "com.github.actions.description"="Formats Java code using Google Java Format"
LABEL "com.github.actions.icon"="mic"
LABEL "com.github.actions.color"="green"

LABEL "homepage"="http://github.com/actions"
LABEL "maintainer"="Clinton <ctpinto27@gmail.com>"

RUN apk update \
    && apk add \
    curl \
    ca-certificates \
    git \
    jq \
    bash \
    python3 \
    py-pip

RUN pip3 install requests

COPY translate-strings.sh /
COPY lib.sh /
COPY gtranslate.py /
COPY translation-config.properties /
ENTRYPOINT ["/translate-strings.sh"]
