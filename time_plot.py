import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams["figure.figsize"] = (10, 3)

x_label1 = ["2", "4", "6", "8", "10", "12"]
x_label2 = ["2", "4", "6", "8", "10", "12", "16", "32", "64", "128", "256", "512"]
y1 = [0.17, 3, 18, 2043, 25200, 86400]
y2 = [0.0005, 0.0013, 0.0024, 0.0038, 0.005, 0.007, 0.013, 0.05, 0.187, 0.7819, 3.18, 8.07]

y1 = [i*1000 for i in y1]
y2 = [i*1000 for i in y2]

plt.grid(linestyle='--', linewidth=0.5)
plt.plot(x_label2, y2, marker="^", color="royalblue", markersize=12)
plt.plot(x_label1, y1, marker="v", color="firebrick", markersize=12)
plt.yscale("log")

#plt.yticks([8, 11, 14, 17, 20, 23, 26], fontsize=15)
plt.xticks(fontsize=15)

plt.ylabel('Time (ms)', fontsize=16)
plt.xlabel('CNs (#)', fontsize=16)
plt.yticks([10**0, 10**2, 10**4, 10**6, 10**8, 10**8.9], fontsize=15)

plt.rcParams.update({'font.size': 18})

legend_elements = [Line2D([0], [0], color='royalblue', lw=3, marker='^', markersize=10, label='Heuristic'),
                        Line2D([0], [0], color='firebrick', lw=3, marker='v', markersize=10, label='Optimal')]
plt.legend(handles=legend_elements, loc="upper right")

plt.savefig("optiaml_x_heuristic_time.pdf", bbox_inches="tight")

plt.show()
