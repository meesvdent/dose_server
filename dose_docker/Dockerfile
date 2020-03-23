# our base image
FROM alpine:3.5

# Add bash
RUN apk add --no-cache bash

# Add ssh
RUN apk --update add openssh-client

# Install git
RUN apk add --no-cache git
RUN git init

# Setup ssh
COPY ./id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# Add ssh key
RUN eval "$(ssh-agent)" \ 
&& echo -e "StrictHostKeyChecking no" >> /etc/ssh/ssh_config \
&& ssh-add /root/.ssh/id_rsa

# Use git with SSH instead of https
RUN git config --global url."git@github.com:".insteadOf "https://github.com/"

# Skip Host verification for git
#RUN echo “StrictHostKeyChecking no “ > /root/.ssh/config

# Get repository
RUN git clone https://github.com/meesvdent/dose_server
