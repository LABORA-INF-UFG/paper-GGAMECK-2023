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
                 XAPPS_CHAIN, CPU_E2, DB_STORAGE, CPU_DB, TOTAL_XAPPS_CHAIN, SDL_ACCESS, xApps_head):
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
    with open('topologies/{}_CRs_new_topology.json'.format(q_CRs)) as json_file:
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
    RIC_json = open("optimization_model/RIC_input.json")
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

    return RIC_parameters(DELAY_RIC_DU, DELAY_RIC_E2, DELAY_RIC_SDL, CPU_RIC, CPU_SDL, CPU_XAPPS,
                          N_XAPPS, XAPPS_CHAIN, CPU_E2, DB_STORAGE, CPU_DB, TOTAL_XAPPS_CHAIN, SDL_ACCESS, xApps_head)


def run_model(q_CRs, q_RUs):
    print("Running...")
    print("-----------------------------------------------------------------------------------------------------------")
    alocation_time_start = time.time()

    read_topology(q_CRs, q_RUs)

    # for l in links:
    #     print(l, links[l].delay)

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
    TOTAL_XAPPS_CHAIN = RDC_cfg.TOTAL_XAPPS_CHAIN
    CPU_XAPPS = RDC_cfg.CPU_XAPPS
    SDL_ACCESS = RDC_cfg.SDL_ACCESS

    xApps_head = RDC_cfg.xApps_head

    # for xApp in range(1, N_XAPPS+1):
    #     for xApp_n in TOTAL_XAPPS_CHAIN[str(xApp)]:
    #         print(SDL_ACCESS[xApp_n])

    mdl = Model(name='Alternative_RIC_allocation', log_output=True)
    # mdl.parameters.emphasis.mip = 2

    # for du in dus:
    #     crs.pop(dus[du].CR)

    i = [(c_RIC, du, e2, sdl, bd) for c_RIC in crs for du in dus for e2 in crs for sdl in crs for bd in crs]

    mdl.x = mdl.binary_var_dict(keys=i, name='x')

    i_xApps = [(du, xApp, cr) for du in dus for xApp in range(1, N_XAPPS+1) for cr in crs]
    mdl.y = mdl.binary_var_dict(keys=i_xApps, name='y')

    u = [c for c in crs]
    mdl.u_RIC = mdl.binary_var_dict(keys=u, name='u_RIC')
    mdl.u_E2 = mdl.binary_var_dict(keys=u, name='u_E2')
    mdl.u_SDL = mdl.binary_var_dict(keys=u, name='u_SDL')
    mdl.u_DB = mdl.binary_var_dict(keys=u, name='u_DB')
    mdl.u_CR = mdl.binary_var_dict(keys=u, name='u_CR')

    u_CR_DU = [(c, du) for c in crs for du in dus]
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
        mdl.add_constraint(mdl.u_RIC[c] >= mdl.sum(mdl.x[it] for it in i if it[0] == c) / len(dus))

        mdl.add_constraint(mdl.u_E2[c] <= mdl.sum(mdl.x[it] for it in i if it[2] == c))
        mdl.add_constraint(mdl.u_E2[c] >= mdl.sum(mdl.x[it] for it in i if it[2] == c) / len(dus))

        mdl.add_constraint(mdl.u_SDL[c] <= mdl.sum(mdl.x[it] for it in i if it[3] == c))
        mdl.add_constraint(mdl.u_SDL[c] >= mdl.sum(mdl.x[it] for it in i if it[3] == c) / len(dus))

        mdl.add_constraint(mdl.u_DB[c] <= mdl.sum(mdl.x[it] for it in i if it[4] == c))
        mdl.add_constraint(mdl.u_DB[c] >= mdl.sum(mdl.x[it] for it in i if it[4] == c) / len(dus))

        mdl.add_constraint(mdl.u_CR[c] <= mdl.u_RIC[c] + mdl.u_E2[c] + mdl.u_SDL[c] + mdl.u_DB[c])
        mdl.add_constraint(mdl.u_CR[c] >= (mdl.u_RIC[c] + mdl.u_E2[c] + mdl.u_SDL[c] + mdl.u_DB[c])/4)

        mdl.add_constraint(mdl.v_CR[c] <= mdl.sum(mdl.y[it] for it in i_xApps if it[2] == c))
        mdl.add_constraint(mdl.v_CR[c] >= mdl.sum(mdl.y[it] for it in i_xApps if it[2] == c)/len(i_xApps))

        for du in dus:
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
    # CUSTO VARIADO RIC
    phy1 = mdl.sum(mdl.u_RIC[c] * crs[c].RIC_cost for c in crs)

    # CUSTO VARIADO E2
    phy2 = mdl.sum(mdl.u_E2[c] * crs[c].E2_cost for c in crs)

    # CUSTO VARIADO SDL
    phy3 = mdl.sum(mdl.u_SDL[c] * crs[c].SDL_cost for c in crs)

    # CUSTO VARIADO DB
    phy4 = mdl.sum(mdl.u_DB[c] * crs[c].DB_cost for c in crs)

    # CUSTO VARIADO xApps
    phy5 = mdl.sum(mdl.v_CR_xApp[(cr, xApp)] * crs[c].xApp_cost for xApp in range(1, N_XAPPS+1) for cr in crs)

    # CONTABILIZA O CUSTO DOS CRs UTILIZADOS FIXO
    phy6 = mdl.sum((mdl.u_CR[cr]) * crs[cr].fixed_cost for cr in crs)

    # MINIMIZA A QUANTIDADE DE RICS
    mdl.minimize(phy1 + phy2 + phy3 + phy4 + phy5 + phy6)

    # mdl.add_constraint(phy1 + phy2 + phy3 + phy4 + phy5 + phy6 >= 1)

    # CADA RIC_MAN POSSUI APENAS UM SDL
    for c in crs:
        cr = c
        mdl.add_constraint(mdl.u_RIC[c] * CPU_RIC +
                           mdl.u_E2[c] * CPU_E2 +
                           mdl.u_SDL[c] * CPU_SDL +
                           mdl.u_DB[c] * CPU_DB +
                           mdl.sum(mdl.v_CR_xApp[(c, xApp_n)] * CPU_XAPPS[str(xApp_n)] for xApp_n in range(1, N_XAPPS + 1)) <= crs[cr].cpu)
        mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if it[4] == crs[cr].id) * DB_STORAGE <= crs[cr].storage)

    # REQUISITO DE DELAY ENTRE RIC E DU DEVEM SER RESPEITADOS
    for it in i:
        mdl.add_constraint(mdl.x[it] * links['({}, {})'.format(it[0], dus[it[1]].CR)].delay <= DELAY_RIC_DU)
        mdl.add_constraint(mdl.x[it] * links['({}, {})'.format(it[0], it[2])].delay <= DELAY_RIC_E2)
        mdl.add_constraint(mdl.x[it] * links['({}, {})'.format(it[0], it[3])].delay <= DELAY_RIC_SDL)

    # LOOP ENTRE DE MENSAGENS INSERT
    # # EXPERIMENT DELAY CONSTRAINT
    # for du in dus:
    #     mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if it[1] == dus[du].id) == 1)
    #     for xApp in range(1, N_XAPPS+1):
    #         mdl.add_constraint(mdl.sum(mdl.x[it1] * (links['({}, {})'.format(dus[it1[1]].CR, it1[2])].delay +
    #                              links['({}, {})'.format(it1[2], it1[3])].delay +
    #                                    links['({}, {})'.format(it1[3], it1[4])].delay) for it1 in i if it1[1] == du)
    #                                +
    #                                mdl.sum(mdl.x[it2] * mdl.sum(mdl.y[it3] * links['({}, {})'.format(it2[2], it3[2])].delay
    #                                                             for it3 in i_xApps if it3[0]==du and it3[1]==xApp)
    #                                        for it2 in i) <= 5)

    # GENERIC DELAY CONTRAINT CODE
    #     i = [(c_RIC, du, e2, sdl, bd) for c_RIC in crs for du in dus for e2 in crs for sdl in crs for bd in crs]
    #     i_xApps = [(du, xApp, cr) for du in dus for xApp in range(1, N_XAPPS+1) for cr in crs]
    for du in dus:
        mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if it[1] == dus[du].id) == 1)
        for xApp in range(1, N_XAPPS+1):
            mdl.add_constraint(mdl.sum(mdl.y[it] for it in i_xApps if it[0] == du and it[1] == xApp) == 1)

        for xApp in range(1, N_XAPPS+1): #     i = (c_RIC, du, e2, sdl, bd)
            mdl.add_constraint(mdl.sum(mdl.x[it] * (links['({}, {})'.format(dus[du].CR, it[2])].delay + links['({}, {})'.format(it[3], it[4])].delay) for it in i if it[1] == du) +
                                   mdl.sum(mdl.y[(du, xApp, c1)] * xApps_head[str(xApp)] * mdl.sum(mdl.u_E2_DU[(c2, du)] * links['({}, {})'.format(c2, c1)].delay for c2 in crs) for c1 in crs) +
                                   mdl.sum(mdl.y[(du, xApp, c1)] * SDL_ACCESS[str(xApp)] * mdl.sum(mdl.u_SDL_DU[(c2, du)] * links['({}, {})'.format(c2, c1)].delay for c2 in crs) for c1 in crs) <= 5)

        # for it1 in i:
        #     for it2 in i_xApps:
        #         if it1[1] == it2[0] == du:
        #             mdl.add_constraint((mdl.x[it1] * links['({}, {})'.format(dus[du].CR, it1[2])].delay) +
        #                                (mdl.y[it2] * xApps_head[str(it2[1])] * links['({}, {})'.format(it1[2], it2[2])].delay) +
        #                                (mdl.sum(mdl.sum(mdl.y[it3] * mdl.y[it4] * links['({}, {})'.format(it3[2], it4[2])].delay
        #                                                 for it3 in i_xApps
        #                                                 for it4 in i_xApps
        #                                                 if it3[1] == xApp_n
        #                                                 and it4[1] == XAPPS_CHAIN[str(xApp_n)]
        #                                                and it3[0] == it4[0] == du)
        #                                         for xApp_n in TOTAL_XAPPS_CHAIN[str(it2[1])])) +
        #                                (mdl.sum(mdl.sum(mdl.x[it1] * mdl.y[it3] * links['({}, {})'.format(it1[3], it3[2])].delay
        #                                                 for it3 in i_xApps
        #                                                 if it3[0] == du
        #                                                 and it3[1] == xApp_n
        #                                                 and SDL_ACCESS[xApp_n] == 1)
        #                                         for xApp_n in TOTAL_XAPPS_CHAIN[str(it2[1])])) +
        #                                (mdl.x[it1] * links['({}, {})'.format(it1[3], it1[4])].delay) <= 5, "first delay cosntraint")

    alocation_time_end = time.time()

    start_time = time.time()
    mdl.solve()
    end_time = time.time()

    print("Alocation Time: {}".format(alocation_time_end - alocation_time_start))
    print("Solver Enlapsed Time: {}".format(end_time - start_time))
    print("FO: ", mdl.solution.get_objective_value())

    RIC_loc = {}
    DUs_RIC = {}
    all_DUs = {}

    for it in v_CR_xApp:
        if mdl.v_CR_xApp[it].solution_value > 0.8:
            print("CR {} used as xApp {}".format(it[0], it[1]))
    for it in i:
        if mdl.x[it].solution_value > 0.8:
            # (c_RIC, du, e2, sdl, bd)
            print("DU {} | RIC {} | E2 {} | SDL {} | DB {}".format(it[1], it[0], it[2], it[3], it[4]))
            DUs_RIC["DU"] = it[1]
            DUs_RIC["RIC"] = it[0]
            DUs_RIC["E2T"] = it[2]
            DUs_RIC["SDL"] = it[3]
            DUs_RIC["DB"] = it[4]

            for it2 in i_xApps:
                if mdl.y[it2].solution_value > 0.8 and it[1] == it2[0]:
                    print("DU {} | xAPP {} | CR {}".format(it2[0], it2[1], it2[2]))
                    DUs_RIC["xApp{}".format(it2[1])] = it2[2]
            all_DUs[str(it[1])] = DUs_RIC.copy()
    solution = {"DUs": []}
    for i in all_DUs:
        solution["DUs"].append(all_DUs[i])

    solution_file = open("solutions/optimal_{}_CRs_{}_RUs.json".format(q_CRs, q_RUs), "w")
    json.dump(solution, solution_file)


if __name__ == '__main__':
    start_all = time.time()
    run_model(q_CRs=12, q_RUs=512)
    end_all = time.time()
    print("TOTAL TIME: {}".format(end_all - start_all))
