import json
import time
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
    def __init__(self, id, CR, closest_CR):
        self.id = id
        self.CR = CR
        self.closest_CR = closest_CR

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
            E2N[du["id"]] = DU(du["id"], du["CR"], du["closest_CR"])


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


def heuristic():
    print("Running...")
    print("-----------------------------------------------------------------------------------------------------------")
    time_start = time.time()

    read_topology()
    RDC_cfg = RDC_config()
    DELAY_RIC_E2 = RDC_cfg.DELAY_RIC_E2
    DELAY_RIC_DU = RDC_cfg.DELAY_RIC_DU
    DELAY_RIC_SDL = RDC_cfg.DELAY_RIC_SDL
    CPU_RIC = RDC_cfg.CPU_RIC
    CPU_E2 = RDC_cfg.CPU_E2
    CPU_SDL = RDC_cfg.CPU_SDL
    N_XAPPS = RDC_cfg.N_XAPPS
    CPU_XAPPS = RDC_cfg.CPU_XAPPS
    MEM_RIC = RDC_cfg.CPU_RIC
    MEM_E2 = RDC_cfg.CPU_E2
    MEM_SDL = RDC_cfg.CPU_SDL
    MEM_XAPPS = RDC_cfg.CPU_XAPPS
    solution = {}

    for du in E2N:
        solution[E2N[du].id] = {"RIC_MAN": E2N[du].closest_CR,
                                "E2T": E2N[du].closest_CR,
                                "SDL": E2N[du].closest_CR,
                                "DB": E2N[du].closest_CR}

        for xApp in range(1, N_XAPPS+1):
            solution[E2N[du].id]["xApp{}".format(xApp)] = E2N[du].closest_CR

    sorted_crs = {k: v for k, v in sorted(crs.items(), key=lambda item: item[1].fixed_cost)}

    used_CRs = {}
    used_CRs["RIC_MAN"] = []
    used_CRs["E2T"] = []
    used_CRs["SDL"] = []
    used_CRs["DB"] = []

    for xApp in range(1, N_XAPPS + 1):
        used_CRs["xApp{}".format(xApp)] = []

    # CENTRALIZANDO RIC DE ACORDO COM O CUSTO FIXO DOS CRS - LISTA ORDENADA
    for du in E2N:
        flag = True
        for cr in used_CRs["RIC_MAN"]:
            feasible = True

            if links[str((E2N[du].CR, crs[cr].id))].delay >= DELAY_RIC_DU:
                feasible = False
            if links[str((solution[E2N[du].id]["E2T"], crs[cr].id))].delay > DELAY_RIC_E2:
                feasible = False
            if links[str((solution[E2N[du].id]["SDL"], crs[cr].id))].delay > DELAY_RIC_SDL:
                feasible = False

            if feasible:
                flag = False
                solution[E2N[du].id]["RIC_MAN"] = crs[cr].id
                break

        if flag:
            for cr in sorted_crs:
                feasible = True
                if links[str((E2N[du].CR, crs[cr].id))].delay >= DELAY_RIC_DU:
                    feasible = False
                if links[str((solution[E2N[du].id]["E2T"], crs[cr].id))].delay > DELAY_RIC_E2:
                    feasible = False
                if links[str((solution[E2N[du].id]["SDL"], crs[cr].id))].delay > DELAY_RIC_SDL:
                    feasible = False

                if crs[cr].cpu - CPU_RIC < 0:
                    feasible = False
                if crs[cr].memory - MEM_RIC < 0:
                    feasible = False

                if feasible:
                    solution[E2N[du].id]["RIC_MAN"] = crs[cr].id
                    crs[cr].cpu -= CPU_RIC
                    crs[cr].memory -= MEM_RIC
                    if crs[cr].id not in used_CRs["RIC_MAN"]:
                        used_CRs["RIC_MAN"].append(crs[cr].id)
                    break
    # CENTRALIZANDO E2 TERMS
    for du in E2N:
        flag = True
        for cr in used_CRs["E2T"]:
            feasible = True
            if links[str((solution[E2N[du].id]["RIC_MAN"], crs[cr].id))].delay > DELAY_RIC_E2:
                feasible = False

            for xApp in range(1, N_XAPPS + 1):
                if links[str((E2N[du].CR, crs[cr].id))].delay + links[str((crs[cr].id, E2N[du].CR))].delay + \
                        links[str((crs[cr].id, solution[E2N[du].id]["xApp{}".format(xApp)]))].delay + \
                        links[str((solution[E2N[du].id]["xApp{}".format(xApp)], crs[cr].id))].delay + \
                        links[str((solution[E2N[du].id]["xApp{}".format(xApp)], solution[E2N[du].id]["SDL"]))].delay + \
                        links[str((solution[E2N[du].id]["SDL"], solution[E2N[du].id]["xApp{}".format(xApp)]))].delay > 10:
                    feasible = False

            if feasible:
                flag = False
                solution[E2N[du].id]["E2T"] = crs[cr].id
                break

        if flag:
            for cr in sorted_crs:
                feasible = True
                if links[str((solution[E2N[du].id]["RIC_MAN"], crs[cr].id))].delay > DELAY_RIC_E2:
                    feasible = False

                for xApp in range(1, N_XAPPS+1):
                    if links[str((E2N[du].CR, crs[cr].id))].delay + links[str((crs[cr].id, E2N[du].CR))].delay + \
                            links[str((crs[cr].id, solution[E2N[du].id]["xApp{}".format(xApp)]))].delay + \
                            links[str((solution[E2N[du].id]["xApp{}".format(xApp)], crs[cr].id))].delay + \
                            links[str((solution[E2N[du].id]["xApp{}".format(xApp)], solution[E2N[du].id]["SDL"]))].delay + \
                            links[str((solution[E2N[du].id]["SDL"], solution[E2N[du].id]["xApp{}".format(xApp)]))].delay > 10:
                        feasible = False

                if crs[cr].cpu - CPU_E2 < 0:
                    feasible = False

                if crs[cr].memory - MEM_E2 < 0:
                    feasible = False

                if feasible:
                    solution[E2N[du].id]["E2T"] = crs[cr].id
                    crs[cr].cpu -= CPU_E2
                    crs[cr].memory -= MEM_E2
                    if crs[cr].id not in used_CRs["E2T"]:
                        used_CRs["E2T"].append(crs[cr].id)
                    break

    # CENTRALIZANDO xApps
    for xApp in range(1, N_XAPPS + 1):
        for du in E2N:
            flag = True
            for cr in used_CRs["xApp{}".format(xApp)]:
                feasible = True

                if links[str((E2N[du].CR, solution[E2N[du].id]["E2T"]))].delay + \
                        links[str((solution[E2N[du].id]["E2T"], E2N[du].CR))].delay +\
                        links[str((solution[E2N[du].id]["E2T"], crs[cr].id))].delay + \
                        links[str((crs[cr].id, solution[E2N[du].id]["E2T"]))].delay + \
                        links[str((crs[cr].id, solution[E2N[du].id]["SDL"]))].delay + \
                        links[str((solution[E2N[du].id]["SDL"], crs[cr].id))].delay > 10:
                    feasible = False

                if feasible:
                    flag = False
                    solution[E2N[du].id]["xApp{}".format(xApp)] = crs[cr].id
                    break

            if flag:
                for cr in sorted_crs:
                    feasible = True

                    if links[str((E2N[du].CR, solution[E2N[du].id]["E2T"]))].delay + \
                            links[str((solution[E2N[du].id]["E2T"], E2N[du].CR))].delay + \
                            links[str((solution[E2N[du].id]["E2T"], crs[cr].id))].delay + \
                            links[str((crs[cr].id, solution[E2N[du].id]["E2T"]))].delay + \
                            links[str((crs[cr].id, solution[E2N[du].id]["SDL"]))].delay + \
                            links[str((solution[E2N[du].id]["SDL"], crs[cr].id))].delay > 10:
                        feasible = False

                    if crs[cr].cpu - CPU_XAPPS["{}".format(xApp)] < 0:
                        feasible = False

                    if crs[cr].memory - MEM_XAPPS["{}".format(xApp)] < 0:
                        feasible = False

                    if feasible:
                        solution[E2N[du].id]["xApp{}".format(xApp)] = crs[cr].id
                        crs[cr].cpu -= CPU_XAPPS["{}".format(xApp)]
                        crs[cr].memory -= MEM_XAPPS["{}".format(xApp)]
                        if crs[cr].id not in used_CRs["xApp{}".format(xApp)]:
                            used_CRs["xApp{}".format(xApp)].append(crs[cr].id)
                        break

    # CENTRALIZANDO SDL
    for du in E2N:
        flag = True
        for cr in used_CRs["SDL"]:
            feasible = True
            if links[str((solution[E2N[du].id]["RIC_MAN"], crs[cr].id))].delay > DELAY_RIC_SDL:
                feasible = False

            for xApp in range(1, N_XAPPS + 1):
                if links[str((E2N[du].CR, solution[E2N[du].id]["E2T"]))].delay + \
                        links[str((solution[E2N[du].id]["E2T"], E2N[du].CR))].delay + \
                        links[str((solution[E2N[du].id]["E2T"], solution[E2N[du].id]["xApp{}".format(xApp)]))].delay +\
                        links[str((solution[E2N[du].id]["xApp{}".format(xApp)], solution[E2N[du].id]["E2T"]))].delay +\
                        links[str((solution[E2N[du].id]["xApp{}".format(xApp)], crs[cr].id))].delay + \
                        links[str((crs[cr].id, solution[E2N[du].id]["xApp{}".format(xApp)]))].delay > 10:
                    feasible = False

            if feasible:
                flag = False
                solution[E2N[du].id]["SDL"] = crs[cr].id
                break

        if flag:
            for cr in sorted_crs:
                feasible = True
                if links[str((solution[E2N[du].id]["RIC_MAN"], crs[cr].id))].delay > DELAY_RIC_SDL:
                    feasible = False

                for xApp in range(1, N_XAPPS + 1):
                    if links[str((E2N[du].CR, solution[E2N[du].id]["E2T"]))].delay + \
                            links[str((solution[E2N[du].id]["E2T"], E2N[du].CR))].delay + \
                            links[str((solution[E2N[du].id]["E2T"], solution[E2N[du].id]["xApp{}".format(xApp)]))].delay + \
                            links[str((solution[E2N[du].id]["xApp{}".format(xApp)], solution[E2N[du].id]["E2T"]))].delay + \
                            links[str((solution[E2N[du].id]["xApp{}".format(xApp)], crs[cr].id))].delay + \
                            links[str((crs[cr].id, solution[E2N[du].id]["xApp{}".format(xApp)]))].delay > 10:
                        feasible = False

                if crs[cr].cpu - CPU_SDL < 0:
                    feasible = False

                if crs[cr].memory - MEM_SDL < 0:
                    feasible = False

                if feasible:
                    solution[E2N[du].id]["SDL"] = crs[cr].id
                    crs[cr].cpu -= CPU_SDL
                    crs[cr].memory -= MEM_SDL
                    if crs[cr].id not in used_CRs["SDL"]:
                        used_CRs["SDL"].append(crs[cr].id)
                    break
    # CENTRALIZANDO DB
    for du in E2N:
        solution[E2N[du].id]["DB"] = solution[E2N[du].id]["SDL"]

    total_cost = 0
    used_CRs = []
    used_CRs_RIC = []
    used_CRs_E2T = []
    used_CRs_SDL = []
    used_CRs_DB = []
    used_CRs_xApp = {}
    for xApp in range(1, N_XAPPS+1):
        used_CRs_xApp["xApp{}".format(xApp)] = []

    for du in solution:
        for i in solution[du]:
            if solution[du][i] not in used_CRs:
                used_CRs.append(solution[du][i])
                total_cost += crs[solution[du][i]].fixed_cost
            if i == "RIC_MAN" and solution[du][i] not in used_CRs_RIC:
                used_CRs_RIC.append(solution[du][i])
                total_cost += crs[solution[du][i]].RIC_cost

            elif i == "E2T" and solution[du][i] not in used_CRs_E2T:
                used_CRs_E2T.append(solution[du][i])
                total_cost += crs[solution[du][i]].E2_cost

            elif i == "SDL" and solution[du][i] not in used_CRs_SDL:
                used_CRs_SDL.append(solution[du][i])
                total_cost += crs[solution[du][i]].SDL_cost

            elif i == "DB" and solution[du][i] not in used_CRs_DB:
                used_CRs_DB.append(solution[du][i])
                total_cost += crs[solution[du][i]].DB_cost

            for xApp in range(1, N_XAPPS+1):
                if i == "xApp{}".format(xApp) and solution[du][i] not in used_CRs_xApp[i]:
                    used_CRs_xApp[i].append(solution[du][i])
                    total_cost += crs[solution[du][i]].xApp_cost

    time_end = time.time()
    print("TOTAL TIME:", time_end - time_start)
    return total_cost, solution


if __name__ == '__main__':
    total_cost, solution = heuristic()
    print("FO:", total_cost)

    new_solution = {"E2Nodes": []}
    for i in solution:
        solution[i]["E2Node"] = i
        new_solution["E2Nodes"].append(solution[i])

    solution_file = open("heuristic_solution.json", "w")
    json.dump(new_solution, solution_file)