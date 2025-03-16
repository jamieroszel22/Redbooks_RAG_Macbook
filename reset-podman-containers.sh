#!/bin/bash
# Podman container reset script

echo "Stopping and removing all Podman containers..."
containers=$(podman ps -a -q)
for container in $containers; do
    echo "Stopping container $container..."
    podman stop $container 2>/dev/null
    echo "Removing container $container..."
    podman rm $container 2>/dev/null
done

echo "Removing all Podman images..."
images=$(podman images -q)
for image in $images; do
    echo "Removing image $image..."
    podman rmi -f $image 2>/dev/null
done

echo "Cleaning up Podman volumes..."
podman volume prune -f

echo "Podman environment has been reset."
echo "To rebuild with the timestamp fix, run ./fix-podman-timestamp.sh"
