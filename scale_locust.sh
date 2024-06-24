#!/bin/bash

# Check for an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <down|number-of-workers>"
    exit 1
fi

# Scale down function
scale_down() {
    kubectl scale deploy locust-inventory-master --replicas=0
    kubectl scale deploy locust-inventory-worker --replicas=0
}

# Scale up function
scale_up() {
    local num_replicas="$1"

    kubectl scale deploy locust-inventory-master --replicas=1

    # Wait for the master pod to be in the Running state
    while [[ $(kubectl get pods -l name=locust-inventory-master -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do 
        echo "Waiting for locust-inventory-master pod to be Running..."
        sleep 1
    done

    kubectl scale deploy locust-inventory-worker --replicas="$num_replicas"
}

# Main
if [ "$1" == "down" ]; then
    scale_down
elif [[ "$1" =~ ^[0-9]+$ ]]; then
    scale_up "$1"
else
    echo "Invalid argument. Use 'down' or provide a number."
    exit 2
fi

