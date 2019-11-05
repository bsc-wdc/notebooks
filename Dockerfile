FROM compss/compss:2.5.1

RUN apt-get update && \
# Apt-get packages
    apt-get install -y --no-install-recommends vim && \
    apt-get clean && \
# Python packages
    pip2 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir --upgrade pip && \
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
    sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
# Remove jenkins user
    userdel -r jenkins

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

# Export environment variables
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV COMPSS_HOME /opt/COMPSs
ENV PYTHONPATH ${COMPSS_HOME}/Bindings/python/:${COMPSS_HOME}/Bindings/bindings-common/lib/:${PYTHONPATH}
ENV LD_LIBRARY_PATH ${COMPSS_HOME}/Bindings/bindings-common/lib/:${COMPSS_HOME}/Runtime/compss-engine.jar:${JAVA_HOME}/jre/lib/amd64/server/:$LD_LIBRARY_PATH
ENV CLASSPATH=$CLASSPATH

# Add environment variables on top of .bashrc
RUN echo "export JAVA_HOME=\${JAVA_HOME}" >> ${HOME}/.compss_vars && \
    echo "export COMPSS_HOME=\${COMPSS_HOME}" >> ${HOME}/.compss_vars && \
    echo "export PYTHONPATH=\${PYTHONPATH}" >> ${HOME}/.compss_vars && \
    echo "export LD_LIBRARY_PATH=\${LD_LIBRARY_PATH}" >> ${HOME}/.compss_vars && \
    echo "export CLASSPATH=\${CLASSPATH}" >> ${HOME}/.compss_vars && \
    cat ${HOME}/.bashrc >> ${HOME}/.compss_vars && \
    mv ${HOME}/.compss_vars ${HOME}/.bashrc
