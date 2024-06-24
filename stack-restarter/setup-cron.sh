#!/bin/bash

# Check if CRON_SCHEDULE is set, otherwise use a default value
: "${CRON_SCHEDULE:=0 * * * *}"

# Get the container ID of the current container
CONTAINER_ID=$(hostname)

# Get the Docker Compose stack name
STACK_NAME=$(curl --unix-socket /var/run/docker.sock -s http://localhost/v1.41/containers/$CONTAINER_ID/json | jq -r '.Config.Labels["com.docker.compose.project"]')

# Create a script to restart the stack
echo "#!/bin/bash"                           > /usr/local/bin/restart-stack.sh
echo "docker-compose -p $STACK_NAME restart" >> /usr/local/bin/restart-stack.sh

# Give execution rights to the restart script
chmod +x /usr/local/bin/restart-stack.sh

# Set up the cron job
echo "$CRON_SCHEDULE /usr/local/bin/restart-stack.sh" > /etc/crontabs/root

# Ensure the cron job file has the correct permissions
chmod 0644 /etc/crontabs/root
