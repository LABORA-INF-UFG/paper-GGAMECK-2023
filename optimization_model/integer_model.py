# -*- coding: utf-8 -*-
import time
import json
from docplex.mp.model import Model
import ast


class link:
    def __init__(self, source, destination, delay):
        self.source = source
        self.destination = destination
        self.delay = delay

    def __str__(self):
        return "({}, {}): {}".format(self.source, self.destination, self.delay)


class CR:
    def __init__(self, id, cpu, storage, fixed_cost, RIC_cost, E2_cost, SDL_cost, DB_cost, xApp_cost):
        self.id = id
        self.cpu = cpu
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
    def __init__(self, DELAY_RIC_DU, DELAY_RIC_E2, DELAY_RIC_SDL, CPU_RIC, CPU_SDL, CPU_XAPPS, N_XAPPS,
                 XAPPS_CHAIN, CPU_E2, DB_STORAGE, CPU_DB):
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


# RIC DEPLOYMENT CONFIGURATION (RDC)
class RDC:
    def __init__(self, RIC_CR, RNIB_CR, xApps_CRs):
        self.RIC_CR = RIC_CR
        self.RNIB_CR = RNIB_CR
        self.xApps_CRs = xApps_CRs


# Global vars
links = {}
crs = {}
dus = {}
delay_min = {}


def read_topology(q_CRs, q_RUs):
    with open('../topologies/topology_{}_CRs_{}_RUs.json'.format(q_CRs, q_RUs)) as json_file:
        json_obj = json.load(json_file)
        json_links = json_obj["links"]

        for l in json_links:
            links[l["link"]] = link(ast.literal_eval(l["link"])[0], ast.literal_eval(l["link"])[1], l["delay"])
            links["({}, {})".format(ast.literal_eval(l["link"])[1], ast.literal_eval(l["link"])[0])] = link(ast.literal_eval(l["link"])[1], ast.literal_eval(l["link"])[0], l["delay"])

        json_CRs = json_obj["CRs"]

        for cr in json_CRs:
            crs[cr["id"]] = CR(cr["id"], cr["cpu"], cr["storage"], cr["fixed_cost"], cr["RIC_cost"], cr["E2_cost"],
                               cr["SDL_cost"], cr["DB_cost"], cr["xApp_cost"])
            links["({}, {})".format(cr["id"], cr["id"])] = link(int(cr["id"]), int(cr["id"]), 0)

        json_DUs = json_obj["DUs"]

        for du in json_DUs:
            dus[du["id"]] = DU(du["id"], du["CR"])


def RDC_config():
    RIC_json = open("../optimization_model/RIC_input.json")
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

    return RIC_parameters(DELAY_RIC_DU, DELAY_RIC_E2, DELAY_RIC_SDL, CPU_RIC, CPU_SDL, CPU_XAPPS,
                          N_XAPPS, XAPPS_CHAIN, CPU_E2, DB_STORAGE, CPU_DB)


def run_model(q_CRs, q_RUs):
    print("Running...")
    print("-----------------------------------------------------------------------------------------------------------")
    alocation_time_start = time.time()

    read_topology(q_CRs, q_RUs)

    RDC_cfg = RDC_config()
    DELAY_RIC_E2 = RDC_cfg.DELAY_RIC_E2
    DELAY_RIC_DU = RDC_cfg.DELAY_RIC_DU
    DELAY_RIC_SDL = RDC_cfg.DELAY_RIC_SDL

    CPU_RIC = RDC_cfg.CPU_RIC
    CPU_E2 = RDC_cfg.CPU_E2
    CPU_SDL = RDC_cfg.CPU_SDL
    DB_STORAGE = RDC_cfg.DB_STORAGE
    CPU_DB = RDC_cfg.CPU_DB

    N_XAPPS = RDC_cfg.N_XAPPS
    XAPPS_CHAIN = RDC_cfg.XAPPS_CHAIN
    TOTAL_XAPPS_CHAIN = {1: [1, 2], 2: []}
    CPU_XAPPS = RDC_cfg.CPU_XAPPS
    SDL_ACCESS = {1: 1, 2: 1}

    xApps_head = {1: 1, 2: 0}

    mdl = Model(name='Integer_RIC_Model', log_output=True)
    # mdl.parameters.emphasis.mip = 2

    i_RM = [du for du in dus]
    mdl.RM = mdl.integer_var_dict(i_RM)

    b_RM = [cr for cr in crs]
    mdl.bRM = mdl.integer_var_dict(b_RM)

    i_E2T = [du for du in dus]
    mdl.E2T = mdl.integer_var_dict(i_E2T)
    i_SDL = [du for du in dus]
    mdl.SDL = mdl.integer_var_dict(i_SDL)
    i_DB = [du for du in dus]
    mdl.DB = mdl.integer_var_dict(i_DB)
    i_xApp = [du for du in dus]
    mdl.xApp = mdl.integer_var_dict(i_xApp)

    # RANGE DA VARIÁVEL DE DECISÃO 0 < X < Q_CRS + 1
    for it in i_RM:
        mdl.add_constraint(mdl.RM[it] >= 1)
        mdl.add_constraint(mdl.RM[it] <= q_CRs)

    for du in i_RM:
        for cr in b_RM:
            mdl.add(mdl.if_then(mdl.RM[du] == cr, mdl.bRM[cr] == du))

    for it in i_E2T:
        mdl.add_constraint(mdl.E2T[it] >= 1)
        mdl.add_constraint(mdl.E2T[it] <= q_CRs)

    for it in i_SDL:
        mdl.add_constraint(mdl.SDL[it] >= 1)
        mdl.add_constraint(mdl.SDL[it] <= q_CRs)

    for it in i_DB:
        mdl.add_constraint(mdl.DB[it] >= 1)
        mdl.add_constraint(mdl.DB[it] <= q_CRs)

    for it in i_xApp:
        mdl.add_constraint(mdl.xApp[it] >= 1)
        mdl.add_constraint(mdl.xApp[it] <= q_CRs)

    for du in i_RM:
        for cr in b_RM:
            print(str((du, cr)))
            mdl.add_constraint(mdl.if_then(links[str((du, cr))].delay <= 1, mdl.RM[du] == cr))

    alocation_time_end = time.time()
    start_time = time.time()
    mdl.solve()
    end_time = time.time()
    print("Alocation Time: {}".format(alocation_time_end - alocation_time_start))
    print("Solver Enlapsed Time: {}".format(end_time - start_time))
    print("FO: ", mdl.solution.get_objective_value())

    print("-------------------------------------------------------------------------")

    for it in i_RM:
        print("E2N {}".format(it), "-> RIC {}".format(mdl.RM[it].solution_value))

    print("-------------------------------------------------------------------------")

    for it in i_E2T:
        print("E2N {}".format(it), "-> E2T {}".format(mdl.RM[it].solution_value))

    print("-------------------------------------------------------------------------")

    for it in i_SDL:
        print("E2N {}".format(it), "-> SDL {}".format(mdl.RM[it].solution_value))

    print("-------------------------------------------------------------------------")

    for it in i_DB:
        print("E2N {}".format(it), "-> DB {}".format(mdl.RM[it].solution_value))

    print("-------------------------------------------------------------------------")

    for it in i_xApp:
        print("E2N {}".format(it), "-> xApp {}".format(mdl.RM[it].solution_value))

    print("-------------------------------------------------------------------------")


if __name__ == '__main__':
    start_all = time.time()
    run_model(q_CRs=4, q_RUs=2)
    end_all = time.time()
    print("TOTAL TIME: {}".format(end_all - start_all))
