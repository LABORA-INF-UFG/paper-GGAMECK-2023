import networkx as nx
import matplotlib.pyplot as plt
import json

links = []
nodes = []
colors = []
shapes = []

q_CRs = 8
q_RUs = 512

for i in range(0, q_CRs+1):
    colors.append("darkorange")

json_obj = json.load(open("heuristic_{}_CRs_{}_RUs.json".format(q_CRs, q_RUs)))

for du in json_obj["DUs"]:
    if (du["RIC"], du["E2T"]) not in links and du["RIC"] != du["E2T"]:
        links.append((du["RIC"], du["E2T"]))
    if (du["E2T"], du["DU"]) not in links and du["E2T"] != du["DU"]:
        links.append((du["E2T"], du["DU"]))
    if (du["E2T"], du["xApp1"]) not in links and du["E2T"] != du["xApp1"]:
        links.append((du["E2T"], du["xApp1"]))
    if (du["E2T"], du["xApp2"]) not in links and du["E2T"] != du["xApp2"]:
        links.append((du["E2T"], du["xApp2"]))
    if (du["xApp1"], du["SDL"]) not in links and du["xApp1"] != du["SDL"]:
        links.append((du["xApp1"], du["SDL"]))
    if (du["xApp2"], du["SDL"]) not in links and du["xApp2"] != du["SDL"]:
        links.append((du["xApp2"], du["SDL"]))
    if (du["SDL"], du["DB"]) not in links and du["SDL"] != du["DB"]:
        links.append((du["SDL"], du["DB"]))

# for du in json_obj["DUs"]:
#     if colors[du["RIC"]] == "darkorange":
#         colors[du["RIC"]] = "black"
#     if colors[du["E2T"]] == "darkorange":
#         colors[du["E2T"]] = "red"
#     if colors[du["SDL"]] == "darkorange":
#         colors[du["SDL"]] = "red"
#     if colors[du["DB"]] == "darkorange":
#         colors[du["DB"]] = "lightgray"
#     if colors[du["xApp1"]] == "darkorange":
#         colors[du["xApp1"]] = "cornflowerblue"
#     if colors[du["xApp2"]] == "darkorange":
#         colors[du["xApp2"]] = "lightsteelblue"

G = nx.Graph()
G.add_edges_from(links)
fig = plt.figure(1, figsize=(12, 8), dpi=60)
nx.draw_networkx(G, node_color=colors, node_shape='s')
plt.savefig("optimal_solution_{}_CRs_topology.pdf".format(q_CRs), bbox_inches="tight")
plt.show()