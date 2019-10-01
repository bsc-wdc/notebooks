FROM compss/compss:2.5.1

RUN pip2 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir --upgrade pip

RUN apt-get update && \
# Apt-get packages
    apt-get install -y --no-install-recommends vim && \
    apt-get clean && \
    pip2 install --no-cache-dir notebook==5.* && \
    pip3 install --no-cache-dir notebook==5.* && \
    pip2 install --no-cache-dir matplotlib && \
    pip3 install --no-cache-dir matplotlib && \
    python2 -m pip install ipykernel && \
    python2 -m ipykernel install --user && \
    python3 -m pip install ipykernel && \
    python3 -m ipykernel install --user && \
    python3 -m pip install dislib && \
# Clean
    sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Remove jenkins user
RUN userdel -r jenkins

# Add user
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}
RUN adduser --disabled-password \
            --gecos "Default user" \
            --uid ${NB_UID} \
            ${NB_USER}

# Copy the contents of our repo to ${HOME}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

# Add environment variables on top of .bashrc
RUN echo "export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64" >> ${HOME}/.compss_vars && \
    echo "export COMPSS_HOME=/opt/COMPSs" >> ${HOME}/.compss_vars && \
    echo "export PYTHONPATH=\${COMPSS_HOME}/Bindings/python/:\${COMPSS_HOME}/Bindings/bindings-common/lib/:\$PYTHONPATH" >> ${HOME}/.compss_vars && \
    echo "export LD_LIBRARY_PATH=\${COMPSS_HOME}/Bindings/bindings-common/lib/:\${COMPSS_HOME}/Runtime/compss-engine.jar:\${JAVA_HOME}/jre/lib/amd64/server/:\$LD_LIBRARY_PATH" >> ${HOME}/.compss_vars && \
    echo "export CLASSPATH=\$CLASSPATH" >> ${HOME}/.compss_vars
RUN cat ${HOME}/.bashrc >> ${HOME}/.compss_vars
RUN mv ${HOME}/.compss_vars ${HOME}/.bashrc
