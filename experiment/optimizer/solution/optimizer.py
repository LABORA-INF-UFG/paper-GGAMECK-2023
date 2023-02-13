from prometheus_api_client import PrometheusConnect
import json
prom = PrometheusConnect(url ="http://r4-infrastructure-prometheus-server.ricplt:80/", disable_ssl=True)
from flask import Flask,request,json
import experiment_model
import heuristic_model
import time

TRIGGER_ALLERT = 'ContainerCpuUsage'

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Webhook for optimization'

#Code to optimal optimization request
@app.route('/optimizer-optimal')
def optimal_heuristic_optimization():
    print('Call optimal optimization')
    generate_input()
    start_all = time.time()
    print('Optimization start')
    solution = experiment_model.run_model()
    end_all = time.time()
    print("TOTAL TIME: {}".format(end_all - start_all))
    return solution

#Code to optimization request
@app.route('/optimizer-heuristic')
def heuristic_optimization():
    print('Call heuristic optimization')
    generate_input()
    start_all = time.time()
    print('Optimization start')
    solution = heuristic_model.run_model()
    end_all = time.time()
    print("TOTAL TIME: {}".format(end_all - start_all))
    return solution

def generate_input():
    json_dict = {"links": [], "CRs": [], "E2N": [
    {
      "id": 5,
      "CR": 5,
      "closest_CR": 5
    },
    {
      "id": 2,
      "CR": 2,
      "closest_CR": 2
    },
    {
      "id": 3,
      "CR": 3,
      "closest_CR": 3
    },
    {
      "id": 4,
      "CR": 4,
      "closest_CR": 4
    }]}

    crs_id_list = []
    CRs_id = []
    links = []

    ###### Takint the ID of each CR ######
    result = prom.get_current_metric_value(metric_name='avg by (kubernetes_io_hostname) (kubelet_node_name)')
    # result = [{'metric': {'kubernetes_io_hostname': 'node4'}, 'value': [1661213104.048, '1']},
    # {'metric': {'kubernetes_io_hostname': 'node3'}, 'value': [1661213104.048, '1']},
    # {'metric': {'kubernetes_io_hostname': 'node1'}, 'value': [1661213104.048, '1']},
    # {'metric': {'kubernetes_io_hostname': 'node2'}, 'value': [1661213104.048, '1']},
    # {'metric': {'kubernetes_io_hostname': 'node5'}, 'value': [1661213104.048, '1']}]
    for i in result:
        cr_id = int(i["metric"]["kubernetes_io_hostname"].replace('node', ''))
        if cr_id == 1:
            pass
        elif cr_id == 2:
            cpu = 9999
            storage = 9999
            memory = 9999
            fixed_cost = 0
            RIC_cost = 2
            E2_cost = 2
            SDL_cost = 1
            DB_cost = 0
            xApp_cost = 1
        elif cr_id == 3 or cr_id == 4:
            cpu = 9999
            storage = 9999
            memory = 9999
            fixed_cost = 10
            RIC_cost = 4
            E2_cost = 4
            SDL_cost = 2
            DB_cost = 0
            xApp_cost = 1
        else:
            cpu = 9999
            storage = 9999
            memory = 9999
            fixed_cost = 20
            RIC_cost = 8
            E2_cost = 8
            SDL_cost = 4
            DB_cost = 0
            xApp_cost = 2
        if cr_id == 1:
            pass
        else: 
            CRs_id.append({"id": cr_id,
                        "cpu": cpu,
                        "storage": storage,
                        "memory": memory,
                        "fixed_cost": fixed_cost,
                        "RIC_cost": RIC_cost,
                        "E2_cost": E2_cost,
                        "SDL_cost": SDL_cost,
                        "DB_cost": DB_cost,
                        "xApp_cost": xApp_cost})


    ###### Taking the available memory in each CR ######

    result = prom.get_current_metric_value(metric_name='avg by (kubernetes_node) (node_memory_MemAvailable_bytes)')
    # result = [{'metric': {'kubernetes_node': 'node1'}, 'value': [1661213812.411, '5247623168']},
    #           {'metric': {'kubernetes_node': 'node5'}, 'value': [1661213812.411, '4904706048']},
    #           {'metric': {'kubernetes_node': 'node4'}, 'value': [1661213812.411, '7234875392']},
    #           {'metric': {'kubernetes_node': 'node2'}, 'value': [1661213812.411, '7115653120']},
    #           {'metric': {'kubernetes_node': 'node3'}, 'value': [1661213812.411, '7428587520']},
    #           {'metric': {}, 'value': [1661213812.411, '6384930816']}]

    for i in result:
        if "kubernetes_node" in i["metric"]:
            id = int(i["metric"]["kubernetes_node"].replace('node', ''))
            for cr in CRs_id:
                if cr["id"] == id:
                    crs_id_list.append(id)
                    cr["memory"] = int(i["value"][1])

    ###### Taking the available CPU in each CR ######

    result = prom.get_current_metric_value(metric_name='sum by (kubernetes_node) (rate(node_cpu_seconds_total{mode="idle"}[1m]))')
    # result = [{'metric': {'kubernetes_node': 'node5'}, 'value': [1661216475.262, '2.852708333333916']},
    #          {'metric': {'kubernetes_node': 'node4'}, 'value': [1661216475.262, '3.871374999997594']},
    #          {'metric': {'kubernetes_node': 'node2'}, 'value': [1661216475.262, '3.8711666666650366']},
    #          {'metric': {'kubernetes_node': 'node3'}, 'value': [1661216475.262, '3.89598376673252']},
    #          {'metric': {}, 'value': [1661216475.262, '17.12462499999841']},
    #          {'metric': {'kubernetes_node': 'node1'}, 'value': [1661216475.262, '2.583999999999999']}]

    for i in result:
        if "kubernetes_node" in i["metric"]:
            id = int(i["metric"]["kubernetes_node"].replace('node', ''))
            for cr in CRs_id:
                if cr["id"] == id:
                    cr["cpu"] = float(i["value"][1])

    ###### Taking links delay from node 3 ######

    for from_node in crs_id_list:
        result = prom.get_current_metric_value(metric_name='sum by (job) (avg_over_time(probe_http_duration_seconds{app_kubernetes_io_instance="blackbox-node'+str(from_node)+'", phase!="resolve", phase!="tls"}[1m]))')
        # result = [{'metric': {'job': 'blackbox-node5'}, 'value': [1661218428.604, '0.0018186399999999998']},
        #         {'metric': {'job': 'blackbox-node2'}, 'value': [1661218428.604, '0.0018372592']},
        #         {'metric': {'job': 'blackbox-node4'}, 'value': [1661218428.604, '0.0019681388']},
        #         {'metric': {'job': 'blackbox-node3'}, 'value': [1661218428.604, '0.0009001745999999999']}]
        for i in result:
            to_node = int(i["metric"]["job"].replace('blackbox-node', ''))
            delay = float(i["value"][1]) * 1000
            if from_node != to_node:
                links.append({"link": "({}, {})".format(from_node, to_node), "delay": delay})

    json_dict["links"] = links
    json_dict["CRs"] = CRs_id

    json.dump(json_dict, open("topology.json", 'w'))

#Main method
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')




#Usage memory by POD:
#PromQL: 
#avg by (pod) (container_memory_usage_bytes{pod=~".*ricplt.*"})
#Python prometheus_api_client
#result = prom.get_current_metric_value(metric_name='avg by (pod) (container_memory_usage_bytes{pod=~".*ricplt.*"})')
#pprint.pprint(result)
#[{'metric': {'pod': 'deployment-ricplt-e2term-alpha-79b6947676-55kf6'}, ##POD e2term memory bytes 22447445.333333332
#  'value': [1661215195.844, '22447445.333333332']},
# {'metric': {'pod': 'deployment-ricplt-e2mgr-64d8cccc4d-nfwgb'},
#  'value': [1661215195.844, '5371221.333333333']},
# {'metric': {'pod': 'deployment-ricplt-vespamgr-66d7fff7c6-dsntp'},
#  'value': [1661215195.844, '38417749.333333336']},
# {'metric': {'pod': 'deployment-ricplt-alarmmanager-5c55d76648-pb8dj'},
#  'value': [1661215195.844, '16667989.333333334']},
# {'metric': {'pod': 'deployment-ricplt-submgr-7ccf6685b7-jbtcz'},
#  'value': [1661215195.844, '20845909.333333332']},
# {'metric': {'pod': 'deployment-ricplt-e2term-opt-e2term-node1-alpha-7497db6587s56f6'},
#  'value': [1661215195.844, '5363712']},
# {'metric': {'pod': 'statefulset-ricplt-dbaas-server-0'},
#  'value': [1661215195.844, '8501930.666666666']},
# {'metric': {'pod': 'deployment-ricplt-o1mediator-5fb64645b8-gvstp'},
#  'value': [1661215195.844, '47327914.666666664']},
# {'metric': {'pod': 'deployment-ricplt-rtmgr-5cc74d8bd8-cm7r8'},
#  'value': [1661215195.844, '13441706.666666666']},
# {'metric': {'pod': 'deployment-ricplt-a1mediator-6db879dc8b-x8bqd'},
#  'value': [1661215195.844, '40617301.333333336']},
# {'metric': {'pod': 'deployment-ricplt-appmgr-674858b486-87kxr'},
#  'value': [1661215195.844, '26436949.333333332']}]

#Usage memory by Group:
#RIC Manager is average + 25%
#PromQL: 
#(sum (avg by (pod) (container_memory_usage_bytes{pod=~".*ricplt.*", pod!="statefulset-ricplt-dbaas-server-0", pod!~".*ricplt-e2term.*"}))) +(sum (avg by (pod) (container_memory_usage_bytes{pod=~".*ricplt.*", pod!="statefulset-ricplt-dbaas-server-0", pod!~".*ricplt-e2term.*"})))/100*25
#Python prometheus_api_client
#result = prom.get_current_metric_value(metric_name='(sum (avg by (pod)\
#     (container_memory_usage_bytes{pod=~".*ricplt.*", pod!="statefulset-ricplt-dbaas-server-0",\
#        pod!~".*ricplt-e2term.*"}))) + (sum (avg by (pod) (container_memory_usage_bytes{pod=~".*ricplt.*",\
#            pod!="statefulset-ricplt-dbaas-server-0", pod!~".*ricplt-e2term.*"})))/100*25')
#pprint.pprint(result)
#[{'metric': {}, 'value': [1662689585.322, '2574301866.666667']}]
#E2Term is average + 25%
#PromQL
#avg by (pod) (container_memory_usage_bytes{pod=~"deployment-ricplt-e2term-alpha.*"}) + (avg by (pod) (container_memory_usage_bytes{pod=~"deployment-ricplt-e2term-alpha.*"}))/100*25
#Python prometheus_api_client
#result = prom.get_current_metric_value(metric_name='avg by (pod) (container_memory_usage_bytes{pod=~"deployment-ricplt-e2term-alpha.*"}) + (avg by (pod)\
#     (container_memory_usage_bytes{pod=~"deployment-ricplt-e2term-alpha.*"}))/100*25')
#pprint.pprint(result)
#[{'metric': {'pod': 'deployment-ricplt-e2term-alpha-6cbc9d5d-s7csv'},
#  'value': [1662689851.382, '20198400']}]
#Database + 25%
#PromQL
#avg by (pod) (container_memory_usage_bytes{pod="statefulset-ricplt-dbaas-server-0"}) + (avg by (pod) (container_memory_usage_bytes{pod="statefulset-ricplt-dbaas-server-0"}))/100*25
#Python prometheus_api_client
#result = prom.get_current_metric_value(metric_name='avg by (pod) (container_memory_usage_bytes{pod="statefulset-ricplt-dbaas-server-0"})\
#    + (avg by (pod) (container_memory_usage_bytes{pod="statefulset-ricplt-dbaas-server-0"}))/100*25')
#pprint.pprint(result)
#[{'metric': {'pod': 'statefulset-ricplt-dbaas-server-0'},
#  'value': [1662690184.045, '8553813.333333334']}]


#CPU Usage by POD:
#PromQL: 
#avg by (pod) (rate(container_cpu_usage_seconds_total{pod=~".*ricplt.*",id!~".*cri-containerd.*"}[1m]))
#Python prometheus_api_client
#result = prom.get_current_metric_value(metric_name='avg by (pod) (rate(container_cpu_usage_seconds_total{pod=~".*ricplt.*",id!~".*cri-containerd.*"}[1m]))')
#pprint.pprint(result)
#[{'metric': {'pod': 'deployment-ricplt-a1mediator-6db879dc8b-x8bqd'},
#  'value': [1661217619.56, '0.0010253612103731683']},
# {'metric': {'pod': 'statefulset-ricplt-dbaas-server-0'},
#  'value': [1661217619.56, '0.004510499987766893']},
# {'metric': {'pod': 'deployment-ricplt-e2term-alpha-79b6947676-55kf6'},
#  'value': [1661217619.56, '0.001461662273517628']},
# {'metric': {'pod': 'deployment-ricplt-vespamgr-66d7fff7c6-dsntp'},
#  'value': [1661217619.56, '0.0019624799810010005']},
# {'metric': {'pod': 'deployment-ricplt-o1mediator-5fb64645b8-gvstp'},
#  'value': [1661217619.56, '0.0007679668570397011']},
# {'metric': {'pod': 'deployment-ricplt-alarmmanager-5c55d76648-pb8dj'},
#  'value': [1661217619.56, '0.00019846558243015322']},
# {'metric': {'pod': 'deployment-ricplt-e2term-opt-e2term-node1-alpha-7497db6587s56f6'},
#  'value': [1661217619.56, '0.0005928581181923712']},
# {'metric': {'pod': 'deployment-ricplt-e2mgr-64d8cccc4d-nfwgb'},
#  'value': [1661217619.56, '0.0004122335590488145']},
# {'metric': {'pod': 'deployment-ricplt-submgr-7ccf6685b7-jbtcz'},
#  'value': [1661217619.56, '0.0002724520690372223']},
# {'metric': {'pod': 'deployment-ricplt-rtmgr-5cc74d8bd8-cm7r8'},
#  'value': [1661217619.56, '0.0003120507248282144']},
# {'metric': {'pod': 'deployment-ricplt-appmgr-674858b486-87kxr'},
#  'value': [1661217619.56, '0.0000263172943680095']}]

#CPU usage by Group:
#RIC Manager is average + 25%
#PromQL
#sum (avg by (pod) (rate(container_cpu_usage_seconds_total{pod=~".*ricplt.*",id!~".*cri-containerd.*",pod!="statefulset-ricplt-dbaas-server-0", pod!~".*ricplt-e2term.*"}[1d]))) + (sum (avg by (pod) (rate(container_cpu_usage_seconds_total{pod=~".*ricplt.*",id!~".*cri-containerd.*",pod!="statefulset-ricplt-dbaas-server-0", pod!~".*ricplt-e2term.*"}[1d]))))/100*25
#Python prometheus_api_client
#result = prom.get_current_metric_value(metric_name='sum (avg by (pod) (rate(container_cpu_usage_seconds_total{pod=~".*ricplt.*",id!~".*cri-containerd.*",pod!="statefulset-ricplt-dbaas-server-0", pod!~".*ricplt-e2term.*"}[1d]))) + (sum (avg by (pod) (rate(container_cpu_usage_seconds_total{pod=~".*ricplt.*",id!~".*cri-containerd.*",pod!="statefulset-ricplt-dbaas-server-0", pod!~".*ricplt-e2term.*"}[1d]))))/100*25')
#pprint.pprint(result)
#[{'metric': {}, 'value': [1662690738.898, '0.006089902264671713']}]
#E2Term is average + 25%
#PromQL
#avg by (pod) (rate(container_cpu_usage_seconds_total{pod=~".*ricplt.*",id!~".*cri-containerd.*",pod=~"deployment-ricplt-e2term-alpha.*"}[1d])) + (avg by (pod) (rate(container_cpu_usage_seconds_total{pod=~".*ricplt.*",id!~".*cri-containerd.*",pod=~"deployment-ricplt-e2term-alpha.*"}[1d])))/100*25
#Python prometheus_api_client
#result = prom.get_current_metric_value(metric_name='avg by (pod) (rate(container_cpu_usage_seconds_total{pod=~".*ricplt.*",\
#    id!~".*cri-containerd.*",pod=~"deployment-ricplt-e2term-alpha.*"}[1d])) + (avg by (pod) (rate(container_cpu_usage_seconds_total{pod=~".*ricplt.*",\
#        id!~".*cri-containerd.*",pod=~"deployment-ricplt-e2term-alpha.*"}[1d])))/100*25')
#pprint.pprint(result)
#[{'metric': {'pod': 'deployment-ricplt-e2term-alpha-6cbc9d5d-s7csv'},
#  'value': [1662691511.029, '0.001796216709005284']}]
#Database + 25%
#PromQL
#avg by (pod) (rate(container_cpu_usage_seconds_total{pod="statefulset-ricplt-dbaas-server-0",id!~".*cri-containerd.*"}[1d])) + (avg by (pod) (rate(container_cpu_usage_seconds_total{pod="statefulset-ricplt-dbaas-server-0",id!~".*cri-containerd.*"}[1d]))) /100*25
#Python prometheus_api_client
#result = prom.get_current_metric_value(metric_name='avg by (pod) (rate(container_cpu_usage_seconds_total{pod="statefulset-ricplt-dbaas-server-0"\
#    ,id!~".*cri-containerd.*"}[1d])) + (avg by (pod) (rate(container_cpu_usage_seconds_total{pod="statefulset-ricplt-dbaas-server-0",id!~".*cri-containerd.*"}[1d]))) /100*25')
#pprint.pprint(result)
#[{'metric': {'pod': 'statefulset-ricplt-dbaas-server-0'},
#  'value': [1662691739.426, '0.005640329611059423']}]