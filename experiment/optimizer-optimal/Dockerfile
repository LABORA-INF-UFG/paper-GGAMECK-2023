FROM leoliveroso/cplex-ubuntu-python36:1.0

#Copy kubectl binary
COPY copy-files/kubectl /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl

#Copy Kubernetes authentication file
RUN mkdir /home/.kube
COPY copy-files/config /home/.kube
ENV KUBECONFIG=/home/.kube/config

COPY optimal_solution/* /home/

WORKDIR /home

RUN pip3 install --no-cache-dir -r requirements.txt

#ENTRYPOINT ["python","-u", "trigger.py"]