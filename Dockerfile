FROM ubuntu:24.04 AS base

ENV SHELL="/bin/bash"
ENV DEBIAN_FRONTEND="noninteractive"
ENV DEBCONF_NONINTERACTIVE_SEEN="true"

RUN apt update \
    && apt install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    inetutils-ping \
    sudo \
    python3 \
    python3-pip \
    vim-nox \
    net-tools \
    telnet \
    git \
    rsync \
    tmux \
    htop \
    jq \
    ripgrep \
    ipmitool \
    dnsutils \
    openssh-client sshpass xauth \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    mv kubectl /usr/local/bin/kubectl && \
    chmod +x /usr/local/bin/kubectl

RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 && \
    chmod 700 get_helm.sh && \
    ./get_helm.sh

RUN curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.29.0/kind-linux-amd64 && chmod +x ./kind && mv ./kind /usr/local/bin/kind

RUN install -m 0755 -d /etc/apt/keyrings && curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt update

RUN  apt-get install docker-ce-cli docker-buildx-plugin docker-compose-plugin

RUN wget https://github.com/derailed/k9s/releases/latest/download/k9s_linux_amd64.deb && dpkg -i k9s_linux_amd64.deb && rm k9s_linux_amd64.deb

RUN curl -LO https://github.com/k8sgpt-ai/k8sgpt/releases/download/v0.4.22/k8sgpt_amd64.deb && dpkg -i k8sgpt_amd64.deb && rm k8sgpt_amd64.deb

WORKDIR /root
COPY . .
