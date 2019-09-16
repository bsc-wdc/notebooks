# PyCOMPSs + Jupyter Tutorial Notebooks

This repository contains all PyCOMPSs related tutorial notebooks.

It is divided into two main folders:

1. **syntax**: Contains the main tutorial notebooks. They cover the syntax and main functionalities of PyCOMPSs.
2. **hands-on**: Contains some example applications and hands-on exercises

## Prerequisites

This notebooks can be used with the **Docker** (recommended for Linux and Mac-OS) or **Virtual Machine** (recommended for Windows) provided by BSC.
Alternatively, they can also been used locally.

* Using **Docker**:
    * Docker
    * Git

* Using **Virtual Machine**:
    * VirtualBox

* For **local** execution:
    * Python 2 or 3
    * COMPSs installation
    * Jupyter (with the desired ipykernel)
    * ipywidgets (only for some hands-on notebooks)
    * numpy (onl for some notebooks)

## Instructions

* Using **Docker**:
    * Run in your machine:
        ```
        git clone https://github.com/bsc-wdc/notebooks.git
        docker pull compss/compss-tutorial:2.5
        # Update the path to the notebooks path in the next command before running it
        docker run --name mycompss -p 8888:8888 -p 8080:8080 -v /PATH/TO/notebooks:/home/notebooks -itd compss/compss-tutorial:2.5
        docker exec -it mycompss /bin/bash
        ```
    * Now that docker is running and you are connected:
        ```
        cd /home/notebooks
        /etc/init.d/compss-monitor start
        jupyter-notebook --no-browser --allow-root --ip=172.17.0.2 --NotebookApp.token=
        ```
    * From local web browser:
        * Open COMPSs monitor: http://localhost:8080/compss-monitor/index.zul
        * Open Jupyter notebook interface: http://localhost:8888/

* Using **Virtual Machine**:
    * Download the OVA from: https://www.bsc.es/research-and-development/software-and-apps/software-list/comp-superscalar/downloads  (*Look for Virtual Appliances section*)
    * Import the OVA from VirtualBox
    * Start the Virtual Machine
        * User: **compss**
        * Password: **compss2019**
    * Open a console and run:
        ```
        git clone https://github.com/bsc-wdc/notebooks.git
        cd notebooks
        /etc/init.d/compss-monitor start
        jupyter-notebook
        ```
    * Open the web browser:
        * Open COMPSs monitor: http://localhost:8080/compss-monitor/index.zul
        * Open Jupyter notebook interface: http://localhost:8888/



## Local Execution instructions

Install all requirements described in **Prerequisites** setion.

Usage:

    git clone https://github.com/bsc-wdc/notebooks.git
    cd notebooks
    /etc/init.d/compss-monitor start
    jupyter-notebook

Then:
   * Open COMPSs monitor: http://localhost:8080/compss-monitor/index.zul
   * Open Jupyter notebook interface: http://localhost:8888/
       * Look for the ```application.ipynb``` of interest.


## Important Notes

It is necessary to **RESTART the python kernel from Jupyter** after the execution of any notebook.

## Troubleshooting

* ISSUE 1: Cannot connect using docker pull.
  REASON: *The docker service is not running*:
```
# Error messsage:
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
# SOLUTION: Restart the docker service:
sudo service docker start
```

* ISSUE 2: The notebooks folder is empty or contains other data using docker. REASON: *The notebooks path in the docker run command is wrong*.
```
# Remove the docker instance and reinstantiate with the appropriate notebooks path
exit
docker stop mycompss
docker rm mycompss
# Pay attention and UPDATE: /PATH/TO in the next command
docker run --name mycompss -p 8888:8888 -p 8080:8080 -v /PATH/TO/notebooks:/home/notebooks -itd compss/compss-tutorial:2.5
# Continue as normal
```

* ISSUE 3: COMPSs does not start in Jupyter.
```
# SOLUTION: Restart the python kernel from Jupyter and 
#           check that there are no compss' python/java processes running. 
```