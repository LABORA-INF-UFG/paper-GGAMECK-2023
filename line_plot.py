import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams["figure.figsize"] = (10, 3)

x_label1 = ["2", "4", "6", "8", "10"]
x_label2 = ["2", "4", "6", "8", "10", "12", "16", "32", "64", "128", "256", "512"]
y1 = [142, 72, 72, 72, 72]
y2 = [142, 142, 142, 72, 72, 72, 72, 72, 72, 72, 72, 22]

plt.grid(linestyle='--', linewidth=0.5)
plt.plot(x_label2, y2, marker="^", color="royalblue", markersize=10)
plt.plot(x_label1, y1, marker="v", color="firebrick", markersize=10)

plt.yticks([10, 50, 90, 130, 170, 210], fontsize=15)
plt.xticks(fontsize=15)

plt.ylabel('Objective Function (#)', fontsize=16)
plt.xlabel('CNs (#)', fontsize=16)

plt.rcParams.update({'font.size': 15})

legend_elements = [Line2D([0], [0], color='royalblue', lw=3, marker='^', markersize=10, label='Heuristic'),
                        Line2D([0], [0], color='firebrick', lw=3, marker='v', markersize=10, label='Optimal')]
# plt.legend(handles=legend_elements, loc="upper right")

plt.savefig("optiaml_x_heuristic.pdf", bbox_inches="tight")

plt.show()