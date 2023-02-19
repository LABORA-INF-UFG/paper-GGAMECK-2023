# RIC-O: Efficient placement of a disaggregated and distributed RAN Intelligent Controller with dynamic clustering of radio nodes

This repository aims to demonstrate the **RIC-O: Efficient placement of a disaggregated and distributed RAN Intelligent Controller with dynamic clustering of radio nodes** solution implementation. In our tests, we used the Ubuntu Server 18.04 and Ubuntu 20.04, with Python 3.6.9, docplex 2.20.204 and the IBM CPLEX version 12.8.0.

- [Description](#description)
- [Topologies](#topologies)
- [Analytical modeling](#analytical-modeling)
- [Real-world experiments](#real-world-experiments)
- [RIC-O Environment Deployment](#ric-o-environment-deployment)
- [Citation](#citation)

## Description
This work proposes the first exact model for positioning Near-Real-Time RAN Intelligent Controller disaggregated functions, named **RIC-O**, as a *Mixed Integer Linear Programming (MILP)* problem. The objective function minimizes the total cost to run a disaggregated and distributed Near-RT RIC. The cost has two parts, a fixed cost corresponding to leasing a CN, which is paid independently of the number of consumed resources, and a variable cost that depends on the number of Near-RT RIC components running on a given node. In this way, each solution represents the Near-RT RIC functions positioning with minimal cost, while satisfying the control-loop latency requirement (10ms) for each E2 Node in the network.

## Topologies
In our theoretical evaluation, we assume as RAN topology a next-generation hierarchical network with 512 E2 nodes organized in three main tiers, with different computing resources and costs. The table below represents the parameters used in this scenario:

![image](https://user-images.githubusercontent.com/15385171/218473556-cbcf5b9a-df75-44a5-9df2-a16f6abd40ef.png)

## Analytical modeling

We first investigate the optimization model scalability, showing that the exact model takes a long time to find the optimal solution, and in cases with a larger number of nodes, the exact model fails to complete the search. On the other hand, our heuristic strategy is very efficient and presents high-quality solutions, however, with no guarantee of optimality.


![image](https://user-images.githubusercontent.com/15385171/218474929-413d8515-5838-4243-bbce-6bbf6e44eba1.png)

## Real-world experiments

In this part of the evaluation, we run the experiments in a scenario with five CNs, which are virtual machines (VMs) with the following configuration: 4 vCPUs, 8 GB RAM, and 50 GB of the virtual disk. One CN represents the cloud node (i.e., c0), and the others represent the edge computing nodes (i.e., cm ∈ C). These CNs are worker nodes in a K8S cluster managed by a master node running a sixth VM with the following configuration: eight vCPUs, 16 GB RAM, and 100 GB of the virtual disk. All VMs are hosted on a DELL PowerEdge M610 server with four Intel Xeon X5660 processors and 192 GB RAM, which runs VMware ESXi 6.7 as the hypervisor.

To illustrate the orchestration capabilities of RIC-O, we designed two scenarios in which the latency-sensitive control loop is disrupted and show how our proposal acts to bring the Near-RT RIC back to normal operation. In the first scenario, RIC-O must deal with a sudden and high increase in the latency of the path used to serve a certain E2 node.

![image](https://user-images.githubusercontent.com/15385171/218475687-241914dc-1747-43a9-9c17-31fa871dd18a.png)

The second scenario is more challenging because RIC-O needs to deal with a CN that becomes unavailable.

![image](https://user-images.githubusercontent.com/15385171/218475842-ad6d58d0-35fd-44ef-869b-3851cbb5cda4.png)

## RIC-O Environment Deployment

To deploy the RIC-O environment some build blocks are required. First, Kubernetes because of the cloud-native nature of o proposal. Second, Near-RT RIC. The third additional component is to provide the required information to RIC-O to calculate the Near-RT RIC VNFs placement. And, by the end the RIC-O components.

### Kubernetes

As of the latest release of O-RAN Near-RT RIC (release f), the recommended version of Kubernetes is v1.21. This version of Kubernetes is also the maximum version required to deploy Near-RT RIC. To deploy that we recommend the use of [Kubespray](https://github.com/kubernetes-sigs/kubespray/) v2.19.1.

### Near-RT RIC

Deploy the Near-RT RIC release f using O-RAN Software Community [documentation](https://docs.o-ran-sc.org/projects/o-ran-sc-ric-plt-ric-dep/en/latest/installation-guides.html). Release F of Near-RT RIC is the sixth release of this open-source software platform for 5G networks, and it includes several new features and improvements.


### Components to monitoring environment resources and latency

We are using two additional Prometheus components to monitor the environment. [Prometheus Node Exporter](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus-node-exporter) to get the status of computer resources of Kubernetes Nodes. [Prometheus Blackbox Exporter](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus-blackbox-exporter) to get the latency between Kubernetes Nodes. This was necessary to add in Prometheus embed in Near-RT RIC some information required by RIC-O.

### RIC-O Components

The RIC-O Components building block includes [RIC-O Optimizer](experiment/optimizer) and [RIC-O Deployer](experiment/deployer) components. We implemented a proof-of-concept prototype of RIC-O to validate and evaluate our proposal. The prototype is described in this section, along with the testbed used for its evaluation. RIC-O Optimizer and RIC-O Deployer were implemented using the Python language. The Monitoring System component comprises the monitoring subsystem (Prometheus) of the Near-RT RIC platform that runs on Kubernetes. 

## Citation

```
@misc{https://doi.org/10.48550/arxiv.2301.02760,
  doi = {10.48550/ARXIV.2301.02760},  
  url = {https://arxiv.org/abs/2301.02760},  
  author = {Almeida, Gabriel M. and Bruno, Gustavo Z. and Huff, Alexandre and Hiltunen, Matti and Duarte, Elias P. and Both, Cristiano B. and Cardoso, Kleber V.},  
  keywords = {Networking and Internet Architecture (cs.NI), FOS: Computer and information sciences, FOS: Computer and information sciences},  
  title = {RIC-O: Efficient placement of a disaggregated and distributed RAN Intelligent Controller with dynamic clustering of radio nodes},  
  publisher = {arXiv},  
  year = {2023},  
  copyright = {Creative Commons Attribution 4.0 International}
}

```
