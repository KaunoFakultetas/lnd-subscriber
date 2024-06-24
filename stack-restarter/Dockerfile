FROM alpine:20240606

# Install dcron, curl, bash, jq, docker-cli, and docker-compose
RUN apk update && \
    apk add dcron curl bash jq docker-cli py-pip docker-compose

# Copy the setup script to the container
COPY setup-cron.sh /usr/local/bin/setup-cron.sh

# Give execution rights to the script
RUN chmod +x /usr/local/bin/setup-cron.sh

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the setup script and then dcron on container startup
CMD /usr/local/bin/setup-cron.sh && crond -f && tail -f /var/log/cron.log
