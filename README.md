# PyCOMPSs + Jupyter Tutorial Notebooks

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/bsc-wdc/notebooks/master?urlpath=/tree/home/jovyan)

## Introduction

This repository contains all PyCOMPSs related tutorial notebooks.

It is divided into three main folders:

1. **syntax**: Contains the main tutorial notebooks. They cover the syntax and main functionalities of PyCOMPSs.
2. **hands-on**: Contains example applications and hands-on exercises.
3. **demos**: Contains demonstration notebooks.


## Contents

- [Prerequisites](#prerequisites)
- [Instructions](#instructions)
- [Local Execution instructions](#local-execution-instructions)
- [Important Notes](#important-notes)
- [Troubleshooting](#troubleshooting)
- [Contact](#contact)

## Prerequisites

This notebooks can be used with the [**pycompss-player**](https://compss.readthedocs.io/en/stable/Sections/08_PyCOMPSs_Player.html) (recommended for Linux and Mac-OS),  **Virtual Machine** provided by BSC (recommended for Windows).
Alternatively, they can also been used locally.

* Using [**pycompss-player**](https://pypi.org/project/pycompss-player/):
    * python3
    * [pycompss-player](https://compss.readthedocs.io/en/stable/Sections/08_PyCOMPSs_Player.html)

* Using **Docker**:
    * Docker
    * Git

* Using **Virtual Machine**:
    * VirtualBox

* For **local** execution:
    * Git
    * Python 2 or 3
    * [COMPSs installation](https://compss.readthedocs.io/en/stable/Sections/01_Installation.html)
    * Jupyter (with the desired ipykernel)
    * ipywidgets (only for some hands-on notebooks)
    * numpy (only for some notebooks)
    * [dislib](https://pypi.org/project/dislib/) (only for some notebooks)

## Instructions

* Using [**pycompss-player**](https://compss.readthedocs.io/en/stable/Sections/08_PyCOMPSs_Player.html):
    * Install docker:
        * Linux: ```apt-get install docker``` (depends on your distribution)
        * Mac-os: direct download from docker.com. You can find instructions here: https://docs.docker.com/docker-for-mac/install/
    * Get COMPSs docker image:
        ```
        docker pull compss/compss-tutorial:2.8
        ```
    * Install *pycompss-player*:
        * Linux:
            ```
            sudo python3 -m pip install pycompss-player
            # or
            python3 -m pip install pycompss-player --user
            ```
        * Mac-os:
            ```
            pip install pycompss-player
            ```
    * Get *tutorials*:
        ```
        git clone https://github.com/bsc-wdc/tutorial_apps.git
        ```
        *Note: If the docker pull command fails be sure you have internet connection, the Docker service is running (sudo service docker start) and your user is in the docker group (sudo usermod -aG docker $USER)*
    * Use *pycompss-player*:
        * Initialize a COMPSs cluster:
            ```
	          pycompss init –i compss/compss-tutorial:2.8
            ```
        * Start Jupyter-notebook:
            ```
            pycompss jupyter
            ```
        * Open a web browser with the address: http://localhost:8888 or http://172.17.0.2:8888
        * Check the [**pycompss-player documentation**](https://compss.readthedocs.io/en/stable/Sections/08_PyCOMPSs_Player.html) for more information.
    * Stop *pycompss-player* after playing with PyCOMPSs:
         ```
         pycompss kill
         ```

* Using **Virtual Machine** (recommended for Windows):
    * Download the OVA from: http://compss.bsc.es/releases/vms/COMPSs-2.8.ova
    * Import the OVA from VirtualBox
    * Start the Virtual Machine
        * User: **compss**
        * Password: **compss2021**
    * Get COMPSs docker image:
        ```
        docker pull compss/compss-tutorial:2.8
        ```
        *Note: If the docker pull command fails be sure you have internet connection, the Docker service is running (sudo service docker start) and your user is in the docker group (sudo usermod -aG docker $USER)*
    * Get *tutorials*:
        ```
        git clone https://github.com/bsc-wdc/tutorial_apps.git
        ```
    * Use *pycompss-player*:
        * Initialize a COMPSs cluster:
            ```
	          pycompss init –i compss/compss-tutorial:2.8
            ```
        * Start Jupyter-notebook:
            ```
            pycompss jupyter
            ```
        * Open a web browser with the address: http://localhost:8888 or http://172.17.0.2:8888
        * Check the [**pycompss-player documentation**](https://compss.readthedocs.io/en/stable/Sections/08_PyCOMPSs_Player.html) for more information.
    * Stop *pycompss-player* after playing with PyCOMPSs:
         ```
         pycompss kill
         ```

* Using **Docker**:
    * Run in your machine:
        ```
        git clone https://github.com/bsc-wdc/notebooks.git
        docker pull compss/compss-tutorial:2.8
        # Update the path to the notebooks path in the next command before running it
        docker run --name mycompss -p 8888:8888 -p 8080:8080 -v /PATH/TO/notebooks:/home/notebooks -itd compss/compss-tutorial:2.8
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


## Local Execution instructions

Install all requirements described in **Prerequisites** setion.

* Usage:
    ```
    git clone https://github.com/bsc-wdc/notebooks.git
    cd notebooks
    /etc/init.d/compss-monitor start
    jupyter-notebook
    ```

* Then:
   * Open COMPSs monitor: http://localhost:8080/compss-monitor/index.zul
   * Open Jupyter notebook interface: http://localhost:8888/
       * Look for the `application.ipynb` of interest.


## Important Notes

**Using COMPSs versions < 2.8**: It is necessary to **RESTART the python kernel from Jupyter** after the execution of any notebook.


## Troubleshooting

* **ISSUE 1:** Cannot connect using docker pull.
    * REASON: *The docker service is not running*:
    ```
    # Error messsage:
    Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
    # SOLUTION: Restart the docker service:
    sudo service docker start
    ```

* **ISSUE 2:** The notebooks folder is empty or contains other data using docker.
    * REASON: *The notebooks path in the docker run command is wrong*.
     ```
    # Remove the docker instance and reinstantiate with the appropriate notebooks path
    exit
    docker stop mycompss
    docker rm mycompss
    # Pay attention and UPDATE: /PATH/TO in the next command
    docker run --name mycompss -p 8888:8888 -p 8080:8080 -v /PATH/TO/notebooks:/home/notebooks -itd compss/compss-tutorial:2.8
    # Continue as normal
    ```

* **ISSUE 3:** COMPSs does not start in Jupyter.
    * REASON: *There are COMPSs' python/java processes running*
    ```
    # SOLUTION: Restart the python kernel from Jupyter and check that there are no COMPSs' python/java processes running.
    ```

* **ISSUE 4:** Numba is not working with the VM or Docker.
    * REASON: *Numba is not installed in the VM or docker*
    ```
    # SOLUTION: Install Numba in the VM/Docker
    #           Open a console in the VM/Docker and follow the next steps.
    # For Python 2:
    sudo python2 -m pip install numba
    # or
    python2 -m pip install numba --user
    # For Python 3:
    sudo python3 -m pip install numba
    # or
    python3 -m pip install numba --user
    ```

* **ISSUE 5:** Matplotlib is not working with the VM or Docker.
    * REASON: *Matplotlib is not installed in the VM or docker*
    ```
    # SOLUTION: Install Matplotlib in the VM/Docker
    #           Open a console in the VM/Docker and follow the next steps.
    # For Python 2:
    sudo python2 -m pip install matplotlib
    # or
    python2 -m pip install matplotlib --user
    # For Python 3:
    sudo python3 -m pip install matplotlib
    # or
    python3 -m pip install matplotlib --user
    ```

* **ISSUE 6:** Can not install dislib. Raises an exception with dependency package.
    * REASON: *enum34 is present in the docker instance*
    ```
    # SOLUTION: Uninstall enum34 from the docker instance
    #           Open a console in the Docker and follow the next steps.
    # For Python 3:
    sudo python3 -m pip uninstall -i enum34
    ```


## Contact

[support-compss@bsc.es](mailto:support-compss@bsc.es)
