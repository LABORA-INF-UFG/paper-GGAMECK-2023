# RIC-O: Efficient placement of a disaggregated and distributed RAN Intelligent Controller with dynamic clustering of radio nodes

This repository aims to demonstrate the **RIC-O: Efficient placement of a disaggregated and distributed RAN Intelligent Controller with dynamic clustering of radio nodes** solution implementation. In our tests we used the Ubuntu Server 18.04 and Ubuntu 20.04, with Python 3.6.9, docplex 2.20.204 and the IBM CPLEX version 12.8.0.

- [Description](#description)
- [Topologies](#topologies)
- [Scenarios](#scenarios)
- [Final Results](#final-results)
- [Citation](#citation)

## Description
This work proposes the first exact model for positioning Near-Real-Time RAN Intelligent Controller disaggregated functions, named **RIC-O**, as a *Mixed Integer Linear Programming (MILP)* problem. The objective function minimizes the total cost to run a disaggregated and distributed Near-RT RIC. The cost has two parts, a fixed cost corresponding to leasing a CN, which is paid independently of the number of consumed resources, and a variable cost that depends on the number of Near-RT RIC components running on a given node. In this way, each solution represents the Near-RT RIC functions positioning with minimal cost, while satisfying the control-loop latency requirement (10ms) for each E2 Node in the network.

## Topologies
In our theorical evaluation we assume as RAN topology a next-generation hierarchical network with 512 E2 nodes organized in three main tiers, with different computing resources and costs. The table bellow represents the parameters used in this scenario:

![image](https://user-images.githubusercontent.com/15385171/218473556-cbcf5b9a-df75-44a5-9df2-a16f6abd40ef.png =250x250)

## Analytical modeling

We first investigate the optimization model scalability, showing that the exact model takes a long time to find the optimal solution, and in cases with a larger number of nodes, the exact model fails to complete the search. On the other hand, our heuristic strategy is very efficient and presents high quality solutions, however, with no guarantee of optimality.


![image](https://user-images.githubusercontent.com/15385171/218474929-413d8515-5838-4243-bbce-6bbf6e44eba1.png)

## Real-world experiments

In this part of the evaluation, we run the experiments in a scenario with five CNs, which are virtual machines (VMs) with the following configuration: 4 vCPUs, 8 GB RAM, and 50 GB of the virtual disk. One CN represents the cloud node (i.e., c0), and the others represent the edge computing nodes (i.e., cm ∈ C). These CNs are worker nodes in a K8S cluster managed by a master node running a sixth VM with the following configuration: eight vCPUs, 16 GB RAM, and 100 GB of the virtual disk. All VMs are hosted on a DELL PowerEdge M610 server with four Intel Xeon X5660 processors and 192 GB RAM, which runs VMware ESXi 6.7 as the hypervisor.

To illustrate the orchestration capabilities of RIC-O, we designed two scenarios in which the latency-sensitive control loop is disrupted and show how our proposal acts to bring the Near-RT RIC back to normal operation. In the first scenario, RIC-O must deal with a sudden and high increase in the latency of the path used to serve a certain E2 node.

![image](https://user-images.githubusercontent.com/15385171/218475687-241914dc-1747-43a9-9c17-31fa871dd18a.png)

The second scenario is more challenging because RIC-O needs to deal with a CN that becomes unavailable.

![image](https://user-images.githubusercontent.com/15385171/218475842-ad6d58d0-35fd-44ef-869b-3851cbb5cda4.png)

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
