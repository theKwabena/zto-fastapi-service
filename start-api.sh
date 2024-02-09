#!/bin/bash

export APP_IMAGE=$1
# NFS Server Details
NFS_SERVER="10.40.1.221"
NFS_SHARE="/mnt/sdb/no-entry"
MOUNT_POINT="/mnt/mailboxes/"

# Check or create mount point
if [ ! -d $MOUNT_POINT ]; then
    echo "----------CREATING MOUNT POINT: $MOUNT_POINT ----------"
    sudo mkdir -p $MOUNT_POINT
    if [ $? -ne 0 ]; then
        echo "AN ERROR OCCURRED CREATING THE MOUNT POINT: $MOUNT_POINT"
        exit 1
    else
      echo "----------MOUNT POINT: $MOUNT_POINT  CREATED SUCCESSFULLY----------"
    fi
fi

# Check if nfs-common is installed
if ! dpkg -l | grep -q nfs-common; then
    echo "nfs-common is not installed. Attempting to install..."
    sudo apt install -y nfs-common
    if [ $? -ne 0 ]; then
        echo "Failed to install nfs-common. Exiting."
        exit 1
    fi
fi

# Check if the nfs volume is mounted.
if mountpoint -q $MOUNT_POINT; then
    echo "............NFS SHARE MOUNTED, SKIPPING MOUNT PROCESS............"
else
    # Attempt to mount the NFS share
    echo "............ATTEMPTING TO MOUNT NFS SHARE............"
    sudo mount $NFS_SERVER:$NFS_SHARE $MOUNT_POINT
    if [ $? -eq 0 ]; then
        echo "NFS share mounted successfully."
    else
        echo "Failed to mount NFS share."
        exit 1
    fi
fi

# Run the web app

echo "---------- STARTING MIGRATE-CLIENT-PYTHON-WEB-API ----------"

echo "Neo4knust!" | docker login dreg.knust.edu.gh -u neo --password-stdin
docker compose -f prod.yaml up --build --detach


