import json
import random

q_CRs = 1024
q_RUs = 1024

lim_HL1 = 10
lim_HL2 = 256

links = []

for i in range(1, q_CRs + 1):
    links.append("(0, {})".format(i))

for i in range(1, q_CRs + 1):
    for j in range(1, q_CRs + 1):
        if i < j:
            links.append("({}, {})".format(i, j))

delays = []
delay_candidates = [1, 2, 2, 3, 3]

for i in range(1, q_CRs + 1):
    if i <= lim_HL1:
        delays.append(4)
    elif i <= lim_HL2:
        delays.append(4 + delay_candidates[random.randrange(0, 5)])
    else:
        delays.append(4 + delay_candidates[random.randrange(0, 5)])

for i in range(1, q_CRs + 1):
    for j in range(1, q_CRs + 1):
        if i < j:
            delays.append(delay_candidates[random.randrange(0, 5)])

topology = {"links": [], "CRs": [], "DUs": []}

for i in range(0, len(links)):
    topology["links"].append({"link": links[i], "delay": delays[i]})

for cr in range(0, q_CRs + 1):
    if cr == 0:
        CR = {"id": cr,
              "cpu": 99999999,
              "storage": 99999999,
              "fixed_cost": 0,
              "RIC_cost": 2,
              "E2_cost": 2,
              "SDL_cost": 1,
              "DB_cost": 1,
              "xApp_cost": 1}
    elif cr <= lim_HL1:
        CR = {"id": cr,
              "cpu": 32,
              "storage": 512,
              "fixed_cost": 10,
              "RIC_cost": 4,
              "E2_cost": 4,
              "SDL_cost": 2,
              "DB_cost": 2,
              "xApp_cost": 1}
    elif cr <= lim_HL2:
        CR = {"id": cr,
              "cpu": 16,
              "storage": 256,
              "fixed_cost": 20,
              "RIC_cost": 8,
              "E2_cost": 8,
              "SDL_cost": 4,
              "DB_cost": 4,
              "xApp_cost": 2}
    else:
        CR = {"id": cr,
              "cpu": 8,
              "storage": 256,
              "fixed_cost": 30,
              "RIC_cost": 16,
              "E2_cost": 16,
              "SDL_cost": 8,
              "DB_cost": 8,
              "xApp_cost": 4}
    topology["CRs"].append(CR)

for i in range(1, q_CRs + 1):
    if i > 0:
        topology["DUs"].append({"id": i, "CR": i, "closest_CR": i})

new_topology_file = open("topology_{}_CRs_{}_RUs.json".format(q_CRs, q_RUs), "w")
json.dump(topology, new_topology_file)