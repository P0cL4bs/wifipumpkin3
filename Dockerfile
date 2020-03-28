FROM ubuntu

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
    && apt-get -y install \
        dnsmasq \
        hostapd \
	    nano \
	    wi \
        ifupdown \
        python3 \
        python3-dev \
        python3-pip \
        iptables \
        net-tools \
        rfkill \
        udev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# copy all files to app folder
COPY . /usr/src/app
WORKDIR /usr/src/app
COPY config/hostapd/hostapd.conf /etc/hostapd/hostapd.conf
RUN pip3 install -r requirements.txt
RUN python3 setup.py install
CMD /bin/bash

