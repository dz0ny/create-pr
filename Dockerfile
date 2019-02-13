FROM python:3.7.2-alpine3.9

LABEL version="1.0.0"
LABEL repository="http://github.com/dz0ny/make-pr"
LABEL homepage="http://github.com/dz0ny/make-pr"
LABEL maintainer="Janez Troha"
LABEL "com.github.actions.name"="Automatic PR"
LABEL "com.github.actions.description"="Automatically creates PR"
LABEL "com.github.actions.icon"="git-pull-request"
LABEL "com.github.actions.color"="purple"

RUN apk --no-cache add jq bash
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt && rm -f /requirements.txt

ADD main.py /main.py
ADD entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
