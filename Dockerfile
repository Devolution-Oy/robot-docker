ARG PYTHON_VERSION
FROM python:3.7.6-stretch

LABEL description="Robot Framework in a Python 3 debian stretch based Docker image"

ARG DEBIAN_FRONTEND=noninteractive

ARG UNAME="robot"
ARG GNAME="robot"
ARG UHOME="/home/robot"
ARG HOST_UID=1000
ARG HOST_GID=1000
ARG SHELL="/bin/bash"

USER root

RUN addgroup --system \
  --gid ${HOST_GID} \
  ${GNAME}

# Robot user, However, for github workflows root is used
RUN adduser --system \
  --uid ${HOST_UID} \
  --ingroup ${GNAME} \
  --disabled-password \
  --home ${UHOME} \
  --shell ${SHELL} \
  ${UNAME}

RUN apt-get -yqq update && \
    apt-get -yqq install gnupg2 && \
    apt-get -yqq install curl unzip zip wget && \
    apt-get -yqq install xvfb && \
    apt-get -yqq install apt-transport-https ca-certificates software-properties-common && \
    # apt-get -yqq install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget && \
    rm -rf /var/lib/apt/lists/*

# Install Chrome WebDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver && \
    ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver

# Install Google Chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get -yqq update && \
    apt-get -yqq install google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*


WORKDIR ${UHOME}
COPY --chown=robot:robot run.py ${UHOME}/.

# Add Tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ENTRYPOINT ["/tini", "--", "xvfb-run", "python3", "run.py"]
