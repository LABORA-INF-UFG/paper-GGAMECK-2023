# -*- coding: utf-8 -*-
import os
import time
import json
from docplex.mp.model import Model
from docplex.cp.modeler import element
import ast


class link:
    def __init__(self, source, destination, delay):
        self.source = source
        self.destination = destination
        self.delay = delay

    def __str__(self):
        return "({}, {}): {}".format(self.source, self.destination, self.delay)


class CR:
    def __init__(self, id, cpu, memory, storage, fixed_cost, RIC_cost, E2_cost, SDL_cost, DB_cost, xApp_cost):
        self.id = id
        self.cpu = cpu
        self.memory = memory
        self.storage = storage
        self.fixed_cost = fixed_cost
        self.RIC_cost = RIC_cost
        self.E2_cost = E2_cost
        self.SDL_cost = SDL_cost
        self.DB_cost = DB_cost
        self.xApp_cost = xApp_cost

    def __str__(self):
        return "ID: {}\tCPU: {}\t STORAGE: {}".format(self.id, self.cpu, self.storage)


class DU:
    def __init__(self, id, CR):
        self.id = id
        self.CR = CR

    def __str__(self):
        return "DU: {}\tCR: {}".format(self.id, self.CR)


class RIC_parameters:
    def __init__(self, DELAY_RIC_DU, DELAY_RIC_E2, DELAY_RIC_SDL, CPU_RIC, CPU_SDL, CPU_XAPPS, MEM_RIC, MEM_SDL,
                 MEM_XAPPS, N_XAPPS, XAPPS_CHAIN, CPU_E2, MEM_E2, DB_STORAGE, CPU_DB, MEM_DB,
                 TOTAL_XAPPS_CHAIN, SDL_ACCESS, xApps_head):
        self.N_XAPPS = N_XAPPS
        self.CPU_RIC = CPU_RIC
        self.DELAY_RIC_DU = DELAY_RIC_DU
        self.CPU_SDL = CPU_SDL
        self.DELAY_RIC_SDL = DELAY_RIC_SDL
        self.CPU_XAPPS = CPU_XAPPS
        self.XAPPS_CHAIN = XAPPS_CHAIN
        self.DELAY_RIC_E2 = DELAY_RIC_E2
        self.CPU_E2 = CPU_E2
        self.DB_STORAGE = DB_STORAGE
        self.CPU_DB = CPU_DB
        self.TOTAL_XAPPS_CHAIN = TOTAL_XAPPS_CHAIN
        self.SDL_ACCESS = SDL_ACCESS
        self.xApps_head = xApps_head
        self.MEM_RIC = MEM_RIC
        self.MEM_E2 = MEM_E2
        self.MEM_SDL = MEM_SDL
        self.MEM_XAPPS = MEM_XAPPS
        self.MEM_DB = MEM_DB


# RIC DEPLOYMENT CONFIGURATION (RDC)
class RDC:
    def __init__(self, RIC_CR, RNIB_CR, xApps_CRs):
        self.RIC_CR = RIC_CR
        self.RNIB_CR = RNIB_CR
        self.xApps_CRs = xApps_CRs


# Global vars
links = {}
crs = {}
E2N = {}
delay_min = {}


def read_topology():
    with open('topology.json') as json_file:
        json_obj = json.load(json_file)
        json_links = json_obj["links"]

        for l in json_links:
            links[l["link"]] = link(ast.literal_eval(l["link"])[0], ast.literal_eval(l["link"])[1], l["delay"])
            links["({}, {})".format(ast.literal_eval(l["link"])[1], ast.literal_eval(l["link"])[0])] = link(ast.literal_eval(l["link"])[1], ast.literal_eval(l["link"])[0], l["delay"])
        json_CRs = json_obj["CRs"]

        for cr in json_CRs:
            crs[cr["id"]] = CR(cr["id"], cr["cpu"], cr["memory"], cr["storage"], cr["fixed_cost"], cr["RIC_cost"], cr["E2_cost"],
                               cr["SDL_cost"], cr["DB_cost"], cr["xApp_cost"])
            links["({}, {})".format(cr["id"], cr["id"])] = link(int(cr["id"]), int(cr["id"]), 0)

        json_E2N = json_obj["E2N"]

        for du in json_E2N:
            E2N[du["id"]] = DU(du["id"], du["CR"])


def RDC_config():
    RIC_json = open("RIC_input.json")
    RIC_config = json.load(RIC_json)

    N_XAPPS = RIC_config["N_XAPPS"]
    CPU_RIC = RIC_config["CPU_RIC"]
    DELAY_RIC_DU = RIC_config["DELAY_RIC_DU"]
    CPU_SDL = RIC_config["CPU_SDL"]
    DELAY_RIC_SDL = RIC_config["DELAY_RIC_SDL"]
    CPU_XAPPS = RIC_config["CPU_XAPPS"]
    XAPPS_CHAIN = RIC_config["XAPPS_CHAIN"]
    DELAY_RIC_E2 = RIC_config["DELAY_RIC_E2"]
    CPU_E2 = RIC_config["CPU_E2"]
    DB_STORAGE = RIC_config["DB_STORAGE"]
    CPU_DB = RIC_config["CPU_DB"]
    TOTAL_XAPPS_CHAIN = RIC_config["TOTAL_XAPPS_CHAIN"]
    SDL_ACCESS = RIC_config["SDL_ACCESS"]
    xApps_head = RIC_config["xApps_HEAD"]
    MEM_RIC = RIC_config["MEM_RIC"]
    MEM_E2 = RIC_config["MEM_E2"]
    MEM_SDL = RIC_config["MEM_SDL"]
    MEM_XAPPS = RIC_config["MEM_XAPPS"]
    MEM_DB = RIC_config["MEM_DB"]

    return RIC_parameters(DELAY_RIC_DU, DELAY_RIC_E2, DELAY_RIC_SDL, CPU_RIC, CPU_SDL, CPU_XAPPS, MEM_RIC, MEM_SDL,
                          MEM_XAPPS, N_XAPPS, XAPPS_CHAIN, CPU_E2, MEM_E2, DB_STORAGE, CPU_DB, MEM_DB,
                          TOTAL_XAPPS_CHAIN, SDL_ACCESS, xApps_head)


def run_model():
    print("Running...")
    print("-----------------------------------------------------------------------------------------------------------")
    alocation_time_start = time.time()
    read_topology()
    RDC_cfg = RDC_config()
    DELAY_RIC_E2 = RDC_cfg.DELAY_RIC_E2
    DELAY_RIC_DU = RDC_cfg.DELAY_RIC_DU
    DELAY_RIC_SDL = RDC_cfg.DELAY_RIC_SDL
    CPU_RIC = RDC_cfg.CPU_RIC
    CPU_E2 = RDC_cfg.CPU_E2
    CPU_SDL = RDC_cfg.CPU_SDL
    CPU_DB = RDC_cfg.CPU_DB
    MEM_RIC = RDC_cfg.MEM_RIC
    MEM_E2 = RDC_cfg.MEM_E2
    MEM_SDL = RDC_cfg.MEM_SDL
    MEM_DB = RDC_cfg.MEM_DB
    N_XAPPS = RDC_cfg.N_XAPPS
    CPU_XAPPS = RDC_cfg.CPU_XAPPS
    MEM_XAPPS = RDC_cfg.MEM_XAPPS
    SDL_ACCESS = RDC_cfg.SDL_ACCESS
    xApps_head = RDC_cfg.xApps_head
    mdl = Model(name='Alternative_RIC_allocation', log_output=False)
    mdl.parameters.emphasis.mip = 2
    i = [(RIC, du, e2, sdl, bd) for RIC in crs for du in E2N for e2 in crs for sdl in crs for bd in crs if sdl == bd]
    mdl.x = mdl.binary_var_dict(keys=i, name='x')
    i_xApps = [(du, xApp, cr) for du in E2N for xApp in range(1, N_XAPPS+1) for cr in crs]
    mdl.y = mdl.binary_var_dict(keys=i_xApps, name='y')
    u = [c for c in crs]
    mdl.u_RIC = mdl.binary_var_dict(keys=u, name='u_RIC')
    mdl.u_E2 = mdl.binary_var_dict(keys=u, name='u_E2')
    mdl.u_SDL = mdl.binary_var_dict(keys=u, name='u_SDL')
    mdl.u_DB = mdl.binary_var_dict(keys=u, name='u_DB')
    mdl.u_CR = mdl.binary_var_dict(keys=u, name='u_CR')
    u_CR_DU = [(c, du) for c in crs for du in E2N]
    mdl.u_RIC_DU = mdl.binary_var_dict(keys=u_CR_DU, name='u_RIC_DU')
    mdl.u_E2_DU = mdl.binary_var_dict(keys=u_CR_DU, name='u_E2_DU')
    mdl.u_SDL_DU = mdl.binary_var_dict(keys=u_CR_DU, name='u_SDL_DU')
    mdl.u_DB_DU = mdl.binary_var_dict(keys=u_CR_DU, name='u_DB_DU')
    v_CR = [c for c in crs]
    mdl.v_CR = mdl.binary_var_dict(keys=v_CR, name="v_CR")
    v_CR_xApp = [(c, xApp) for c in crs for xApp in range(1, N_XAPPS+1)]
    mdl.v_CR_xApp = mdl.binary_var_dict(keys=v_CR_xApp, name="v_CR_xApp")
    for c in crs:
        mdl.add_constraint(mdl.u_RIC[c] <= mdl.sum(mdl.x[it] for it in i if it[0] == c))
        mdl.add_constraint(mdl.u_RIC[c] >= mdl.sum(mdl.x[it] for it in i if it[0] == c) / len(E2N))
        mdl.add_constraint(mdl.u_E2[c] <= mdl.sum(mdl.x[it] for it in i if it[2] == c))
        mdl.add_constraint(mdl.u_E2[c] >= mdl.sum(mdl.x[it] for it in i if it[2] == c) / len(E2N))
        mdl.add_constraint(mdl.u_SDL[c] <= mdl.sum(mdl.x[it] for it in i if it[3] == c))
        mdl.add_constraint(mdl.u_SDL[c] >= mdl.sum(mdl.x[it] for it in i if it[3] == c) / len(E2N))
        mdl.add_constraint(mdl.u_DB[c] <= mdl.sum(mdl.x[it] for it in i if it[4] == c))
        mdl.add_constraint(mdl.u_DB[c] >= mdl.sum(mdl.x[it] for it in i if it[4] == c) / len(E2N))
        mdl.add_constraint(mdl.u_CR[c] <= mdl.u_RIC[c] + mdl.u_E2[c] + mdl.u_SDL[c] + mdl.u_DB[c])
        mdl.add_constraint(mdl.u_CR[c] >= (mdl.u_RIC[c] + mdl.u_E2[c] + mdl.u_SDL[c] + mdl.u_DB[c])/4)
        mdl.add_constraint(mdl.v_CR[c] <= mdl.sum(mdl.y[it] for it in i_xApps if it[2] == c))
        mdl.add_constraint(mdl.v_CR[c] >= mdl.sum(mdl.y[it] for it in i_xApps if it[2] == c)/len(i_xApps))
        for du in E2N:
            mdl.add_constraint(mdl.u_RIC_DU[(c, du)] <= mdl.sum(mdl.x[it] for it in i if it[0] == c and it[1] == du))
            mdl.add_constraint(mdl.u_RIC_DU[(c, du)] >= mdl.sum(mdl.x[it] for it in i if it[0] == c and it[1] == du)/len(i))
            mdl.add_constraint(mdl.u_E2_DU[(c, du)] <= mdl.sum(mdl.x[it] for it in i if it[2] == c and it[1] == du))
            mdl.add_constraint(mdl.u_E2_DU[(c, du)] >= mdl.sum(mdl.x[it] for it in i if it[2] == c and it[1] == du)/len(i))
            mdl.add_constraint(mdl.u_SDL_DU[(c, du)] <= mdl.sum(mdl.x[it] for it in i if it[3] == c and it[1] == du))
            mdl.add_constraint(mdl.u_SDL_DU[(c, du)] >= mdl.sum(mdl.x[it] for it in i if it[3] == c and it[1] == du)/len(i))
            mdl.add_constraint(mdl.u_DB_DU[(c, du)] <= mdl.sum(mdl.x[it] for it in i if it[4] == c and it[1] == du))
            mdl.add_constraint(mdl.u_DB_DU[(c, du)] >= mdl.sum(mdl.x[it] for it in i if it[4] == c and it[1] == du)/len(i))
        for xApp in range(1, N_XAPPS+1):
            mdl.add_constraint(mdl.v_CR_xApp[(c, xApp)] <= mdl.sum(mdl.y[it] for it in i_xApps if it[1] == xApp and it[2] == c))
            mdl.add_constraint(mdl.v_CR_xApp[(c, xApp)] >= mdl.sum(mdl.y[it] for it in i_xApps if it[1] == xApp and it[2] == c)/len(i_xApps))
    phy1 = mdl.sum(mdl.u_RIC[c] * crs[c].RIC_cost for c in crs)
    phy2 = mdl.sum(mdl.u_E2[c] * crs[c].E2_cost for c in crs)
    phy3 = mdl.sum(mdl.u_SDL[c] * crs[c].SDL_cost for c in crs)
    phy4 = mdl.sum(mdl.u_DB[c] * crs[c].DB_cost for c in crs)
    phy5 = mdl.sum(mdl.v_CR_xApp[(cr, xApp)] * crs[cr].xApp_cost for xApp in range(1, N_XAPPS+1) for cr in crs)
    phy6 = mdl.sum((mdl.u_CR[cr] * mdl.v_CR[c]) * crs[cr].fixed_cost for cr in crs)
    mdl.minimize(phy1 + phy2 + phy3 + phy4 + phy5 + phy6)
    mdl.add_constraint(phy1 + phy2 + phy3 + phy4 + phy5 + phy6 >= 1)
    for c in crs:
        cr = c
        mdl.add_constraint(mdl.sum(mdl.min(1, mdl.sum(mdl.x[it] for it in i if it[0] == c and it[3] == sdl)) for sdl in crs) <= 1)
        mdl.add_constraint(mdl.u_RIC[c] * CPU_RIC +
                           mdl.u_E2[c] * CPU_E2 +
                           mdl.u_SDL[c] * CPU_SDL +
                           mdl.u_DB[c] * CPU_DB +
                           mdl.sum(mdl.v_CR_xApp[(c, xApp_n)] * CPU_XAPPS[str(xApp_n)] for xApp_n in range(1, N_XAPPS + 1)) <= crs[cr].cpu)
        mdl.add_constraint(mdl.u_RIC[c] * MEM_RIC +
                           mdl.u_E2[c] * MEM_E2 +
                           mdl.u_SDL[c] * MEM_SDL +
                           mdl.u_DB[c] * MEM_DB +
                           mdl.sum(mdl.v_CR_xApp[(c, xApp_n)] * MEM_XAPPS[str(xApp_n)] for xApp_n in
                                   range(1, N_XAPPS + 1)) <= crs[cr].memory)
    for it in i:
        mdl.add_constraint(mdl.x[it] * links['({}, {})'.format(it[0], E2N[it[1]].CR)].delay <= DELAY_RIC_DU)
        mdl.add_constraint(mdl.x[it] * links['({}, {})'.format(it[0], it[2])].delay <= DELAY_RIC_E2)
        mdl.add_constraint(mdl.x[it] * links['({}, {})'.format(it[0], it[3])].delay <= DELAY_RIC_SDL)
    for du in E2N:
        mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if it[1] == E2N[du].id) == 1)
        for xApp in range(1, N_XAPPS+1):
            mdl.add_constraint(mdl.sum(mdl.y[it] for it in i_xApps if it[0] == du and it[1] == xApp) == 1)
        for xApp in range(1, N_XAPPS+1):
            mdl.add_constraint(mdl.sum(mdl.x[it] * (links['({}, {})'.format(E2N[du].CR, it[2])].delay +
                                                    links['({}, {})'.format(it[2], E2N[du].CR)].delay)
                                       for it in i if it[1] == du) +
                               mdl.sum(mdl.y[(du, xApp, c1)] * xApps_head[str(xApp)] * mdl.sum(mdl.u_E2_DU[(c2, du)] *
                                                   (links['({}, {})'.format(c2, c1)].delay +
                                                    links['({}, {})'.format(c1, c2)].delay)for c2 in crs)for c1 in crs)+
                               mdl.sum(mdl.y[(du, xApp, c1)] * SDL_ACCESS[str(xApp)] * mdl.sum(mdl.u_SDL_DU[(c2, du)] *
                                                   (links['({}, {})'.format(c2, c1)].delay +
                                                    links['({}, {})'.format(c1, c2)].delay) for c2 in crs)for c1 in crs)
                               <= 10, "delay_constraint")
    alocation_time_end = time.time()
    start_time = time.time()
    print("Alocation Time: {}".format(alocation_time_end - alocation_time_start))
    mdl.solve()
    end_time = time.time()
    print("Solver Enlapsed Time: {}".format(end_time - start_time))
    print("FO: ", mdl.solution.get_objective_value())
    all_E2N = {}
    # for it in v_CR_xApp:
    #     if mdl.v_CR_xApp[it].solution_value > 0.8:
    #         print("CR {} used as xApp {}".format(it[0], it[1]))
    for it in i:
        E2N_RIC = {}
        if mdl.x[it].solution_value > 0.8:
            # print("DU {} | RIC {} | E2 {} | SDL {} | DB {}".format(it[1], it[0], it[2], it[3], it[4]))
            E2N_RIC["E2Node"] = it[1]
            E2N_RIC["RIC_MAN"] = it[0]
            E2N_RIC["E2T"] = it[2]
            E2N_RIC["SDL"] = it[3]
            E2N_RIC["DB"] = it[4]
            for it2 in i_xApps:
                if mdl.y[it2].solution_value > 0.8 and it[1] == it2[0]:
                    # print("DU {} | xAPP {} | CR {}".format(it2[0], it2[1], it2[2]))
                    E2N_RIC["xApp{}".format(it2[1])] = it[1]
            all_E2N[str(it[1])] = E2N_RIC
    solution = {"E2Nodes": []}
    for i in all_E2N:
        solution["E2Nodes"].append(all_E2N[i])
    # print(solution)
    solution_file = open("optimal_solution.json", "w")
    json.dump(solution, solution_file)
    return solution


if __name__ == '__main__':
    start_all = time.time()
    run_model()
    end_all = time.time()
    print("TOTAL TIME: {}".format(end_all - start_all))
