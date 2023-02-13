FROM python:3.8.13-alpine3.16

#Copy kubectl binary
COPY copy-files/kubectl /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl

#Copy Kubernetes authentication file
RUN mkdir /home/.kube
COPY copy-files/config /home/.kube
ENV KUBECONFIG=/home/.kube/config

#Install trigger application dependencies
RUN pip install flask

#Copy trigger application
COPY trigger.py trigger.py 


ENTRYPOINT ["python","-u", "trigger.py"]