import json
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams["figure.figsize"] = (10, 3)

x_optimal = ["2", "4", "6", "8", "10"]
x_heuristic = ["2", "4", "6", "8", "10", "12", "16", "32", "64", "128", "256", "512"]

# taking optimal values
y_xApps_optimal = []
y_E2T_optimal = []
y_SDL_optimal = []
y_DB_optimal = []
y_RIC_optimal = []

print("Taking Optimal Values")
xApps_optimal = {}
xApp1_optimal = {}
xApp2_optimal = {}
E2T_optimal = {}
SDL_optimal = {}
DB_optimal = {}
RIC_man = {}
for qCRs in [2, 4, 6, 8, 8]:
    print("qCRs", qCRs)
    xApp1_optimal[qCRs] = []
    xApp2_optimal[qCRs] = []
    xApps_optimal[qCRs] = []
    E2T_optimal[qCRs] = []
    SDL_optimal[qCRs] = []
    DB_optimal[qCRs] = []
    RIC_man[qCRs] = []
    jsonObj = json.load(open("solutions/optimal_{}_CRs_512_RUs.json".format(qCRs)))
    for du in jsonObj["DUs"]:
        if du["xApp1"] not in xApp1_optimal[qCRs]:
            xApp1_optimal[qCRs].append(du["xApp1"])
            xApps_optimal[qCRs].append(du["xApp1"])
        if du["xApp2"] not in xApp2_optimal[qCRs]:
            xApp2_optimal[qCRs].append(du["xApp2"])
            xApps_optimal[qCRs].append(du["xApp2"])
        if du["E2T"] not in E2T_optimal[qCRs]:
            E2T_optimal[qCRs].append(du["E2T"])
        if du["SDL"] not in SDL_optimal[qCRs]:
            SDL_optimal[qCRs].append(du["SDL"])
        if du["DB"] not in DB_optimal[qCRs]:
            DB_optimal[qCRs].append(du["DB"])
        if du["RIC"] not in RIC_man[qCRs]:
            RIC_man[qCRs].append(du["RIC"])

    y_xApps_optimal.append(len(xApps_optimal[qCRs]))
    y_E2T_optimal.append(len(E2T_optimal[qCRs]))
    y_SDL_optimal.append(len(SDL_optimal[qCRs]))
    y_DB_optimal.append(len(DB_optimal[qCRs]))
    y_RIC_optimal.append(len(RIC_man[qCRs]))

# taking heuristic values
y_xApps_heuristic = []
y_E2T_heuristic = []
y_SDL_heuristic = []
y_DB_heuristic = []
y_RIC_heuristic = []

print("Taking heuristic Values")
xApps_heuristic = {}
xApp1_heuristic = {}
xApp2_heuristic = {}
E2T_heuristic = {}
SDL_heuristic = {}
DB_heuristic = {}
RIC_man_heu = {}
for qCRs in [2, 4, 6, 8, 10, 12, 16, 32, 64, 128, 256, 512]:
    print("qCRs", qCRs)
    xApp1_heuristic[qCRs] = []
    xApp2_heuristic[qCRs] = []
    xApps_heuristic[qCRs] = []
    E2T_heuristic[qCRs] = []
    SDL_heuristic[qCRs] = []
    DB_heuristic[qCRs] = []
    RIC_man_heu[qCRs] = []
    jsonObj = json.load(open("solutions/heuristic_{}_CRs_512_RUs.json".format(qCRs)))
    for du in jsonObj["DUs"]:
        if du["xApp1"] not in xApp1_heuristic[qCRs]:
            xApp1_heuristic[qCRs].append(du["xApp1"])
            xApps_heuristic[qCRs].append(du["xApp1"])
        if du["xApp2"] not in xApp2_heuristic[qCRs]:
            xApp2_heuristic[qCRs].append(du["xApp2"])
            xApps_heuristic[qCRs].append(du["xApp2"])
        if du["E2T"] not in E2T_heuristic[qCRs]:
            E2T_heuristic[qCRs].append(du["E2T"])
        if du["SDL"] not in SDL_heuristic[qCRs]:
            SDL_heuristic[qCRs].append(du["SDL"])
        if du["DB"] not in DB_heuristic[qCRs]:
            DB_heuristic[qCRs].append(du["DB"])
        if du["RIC"] not in RIC_man_heu[qCRs]:
            RIC_man_heu[qCRs].append(du["RIC"])

    y_xApps_heuristic.append(len(xApps_heuristic[qCRs]))
    y_E2T_heuristic.append(len(E2T_heuristic[qCRs]))
    y_SDL_heuristic.append(len(SDL_heuristic[qCRs]))
    y_DB_heuristic.append(len(DB_heuristic[qCRs]))
    y_RIC_heuristic.append(len(RIC_man_heu[qCRs]))

plt.grid(linestyle='--', linewidth=0.5)
plt.plot(x_optimal, y_xApps_optimal, marker="s", color="firebrick", markersize=10)
plt.plot(x_heuristic, y_xApps_heuristic, marker="s", color="royalblue", markersize=12, fillstyle='none', markeredgewidth=2)

plt.plot(x_optimal, y_E2T_optimal, marker="o", color="firebrick", markersize=8)
plt.plot(x_heuristic, y_E2T_heuristic, marker="o", color="royalblue", markersize=9, fillstyle='none', markeredgewidth=2)

#
plt.yticks([0, 1, 2, 3, 4, 5], fontsize=15)
plt.xticks(fontsize=15)
#
plt.ylabel('Instances (#)', fontsize=16)
plt.xlabel('CNs (#)', fontsize=16)
# # plt.yticks([10**0, 10**2, 10**4, 10**6, 10**8, 10**10], fontsize=15)
#
plt.rcParams.update({'font.size': 18})
#
legend_elements = [Line2D([0], [0], color='royalblue', lw=0, markersize=0, label='Heuristic'),
                   Line2D([0], [0], color='firebrick', lw=0, markersize=0, label='Optimal'),
                   Line2D([0], [0], color='royalblue', lw=2, markersize=10, marker='s', label='xApps', fillstyle='none', markeredgewidth=2),
                   Line2D([0], [0], color='firebrick', lw=2, markersize=10, marker='s', label='xApps'),
                   Line2D([0], [0], color='royalblue', lw=2, markersize=10, marker='o', label='E2T', fillstyle='none', markeredgewidth=2),
                   Line2D([0], [0], color='firebrick', lw=2, markersize=10, marker='o', label='E2T')]
plt.legend(handles=legend_elements, loc="upper right", ncol=3)
plt.savefig("functions.pdf", bbox_inches="tight")
plt.show()
