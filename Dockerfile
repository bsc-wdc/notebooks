FROM compss/compss-tutorial:3.1

RUN apt-get update && \
# Apt-get packages
    apt-get install -y --no-install-recommends vim && \
    apt-get clean && \
# Python packages
    pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir notebook==5.* && \
    pip3 install --no-cache-dir graphviz && \
    python3 -m pip install ipykernel && \
    python3 -m ipykernel install --user && \
    # Dislib requirements:
    python3 -m pip install scikit-learn>=1.0.2 && \
    python3 -m pip install scipy>=1.3.0 && \
    python3 -m pip install numpy==1.18.1 && \
    python3 -m pip install numpydoc>=0.8.0 && \
    python3 -m pip install cvxpy>=1.1.5 && \
    python3 -m pip install cbor2>=5.4.0 && \
    python3 -m pip install pandas>=0.24.2 && \
    python3 -m pip install matplotlib>=2.2.3 && \
    # Dislib:
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
