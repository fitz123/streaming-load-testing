## Introduction
Instructions for using the stress-test utility for streaming, emulating load close to real users.
Repository: [https://github.com/fitz123/streaming-load-testing/tree/master](https://github.com/fitz123/streaming-load-testing/tree/master)

## Component Description
The main framework is locust. It has a client-server architecture. 
The master controls a pool of workers, displays, and aggregates results. 
Each worker executes the script [hls_player.py](https://github.com/fitz123/streaming-load-testing/blob/master/load_generator/locustfiles/hls_player.py).
Each worker uses 1 core. Scaling is achieved through horizontal scaling of workers.
The build is done in Docker containers.
Kubernetes is used for deployment, as it is the most convenient way to scale across multiple servers and orchestrate the launch of workers across servers.

## How to Use
Connect via SSH and forward the port:
    
    ssh -L 8089:10.98.0.201:8089 -J serveradmin@27.254.211.58 serveradmin@10.98.0.201

login into ninja user to use environment

    sudo su ninja

The addresses, server port, and stream link are set in the files `locust-master-deployment.yaml` and `locust-worker-deployment.yaml`. 
After changing them, deploy the new versions to Kubernetes using the command:
    
    k apply -f streaming-load-testing/locust-master-deployment.yaml -f streaming-load-testing/locust-worker-deployment.yaml

To start and stop the system, there is a script. You need to run as many workers as there are cores available on the worker servers. For example, if we have 240 cores, to launch 240 workers and the master, use the command:
    
    ./scale_locust.sh 240

To stop the system:
    
    ./scale_locust.sh down

This will shut down all workers and the master.

After starting the workers, open the master's web interface at https://localhost:8089/ and start the test.

