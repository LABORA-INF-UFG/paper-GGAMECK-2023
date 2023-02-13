#!/bin/bash
helm upgrade --install blackbox-node1 prometheus-community/prometheus-blackbox-exporter -f values-blackbox1.yaml -n ricinfra
helm upgrade --install blackbox-node2 prometheus-community/prometheus-blackbox-exporter -f values-blackbox2.yaml -n ricinfra
helm upgrade --install blackbox-node3 prometheus-community/prometheus-blackbox-exporter -f values-blackbox3.yaml -n ricinfra
helm upgrade --install blackbox-node4 prometheus-community/prometheus-blackbox-exporter -f values-blackbox4.yaml -n ricinfra
helm upgrade --install blackbox-node5 prometheus-community/prometheus-blackbox-exporter -f values-blackbox5.yaml -n ricinfra 
helm upgrade --install node-exporter prometheus-community/prometheus-node-exporter  -n ricinfra 

