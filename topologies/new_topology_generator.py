import json
import random


def topologyFileReader():
    """
    Reads the base topology (512 CRs and RUs/E2N) file and returns its Json object
    """
    return json.load(open("topology_512_CRs_512_RUs.json"))


def CRsRandomSelection(proportion):
    """
    Randomly selects the CNs based on the new topology proportion
    """
    HL1 = random.sample([i for i in range(1, 6)], proportion[0])
    HL2 = random.sample([i for i in range(6, 21)], proportion[1])
    HL3 = random.sample([i for i in range(21, 513)], proportion[2])

    return HL1, HL2, HL3


def creatingNewCRsObj(baseTopoCRs, HL1, HL2, HL3):
    """
    Returns a list (json format) with the CRs datas from the base topology
    """
    newCNs = []
    for cr in baseTopoCRs:
        if cr["id"] in HL1 + HL2 + HL3 + [0]:
            newCNs.append(cr)
    return newCNs


def AllLinksLatency(linksLatency):
    """
    Returns a dict with all links as keys and its latency. This is important to take a link latency in O(1) complexity
    Also returns a dict with the higher delay for each CR selected
    """
    delays = {}
    for l in linksLatency:
        delays[l["link"]] = l["delay"]
    return delays


def E2NodeCRsSelection(baseTopoDUs, newCRsList, AllLinksLatency):
    """
    Return a dict with the closest selected CR for each E2Node in the base topology
    """
    nextCR = {}
    higherLatencyCRs = {}
    for cn in newCRsList:
        higherLatencyCRs[cn] = 0
    for e2n in baseTopoDUs:
        minDelay = float('inf')
        for cn in newCRsList:
            if "({}, {})".format(e2n["CR"], cn) in AllLinksLatency.keys():
                if AllLinksLatency["({}, {})".format(e2n["CR"], cn)] < minDelay:
                    minDelay = AllLinksLatency["({}, {})".format(e2n["CR"], cn)]
                    chosenCN = cn
            else:
                if e2n["CR"] == cn:
                    minDelay = 0
                    chosenCN = cn
                    break
                elif AllLinksLatency["({}, {})".format(cn, e2n["CR"])] < minDelay:
                    minDelay = AllLinksLatency["({}, {})".format(cn, e2n["CR"])]
                    chosenCN = cn
        if higherLatencyCRs[chosenCN] < minDelay:
            higherLatencyCRs[chosenCN] = minDelay
        nextCR[e2n["id"]] = {"CN": chosenCN, "delay": minDelay}

    return nextCR, higherLatencyCRs


def creatingNewLinks(HL1, HL2, HL3, linksLatency, higherLatencyCRs):
    """
    Returns a complete set of links considering the CNs selected its links latency plus the E2N higher latency
    """
    newLinks = []
    # taking delay between cloud and each CN selected
    for cn in HL1 + HL2 + HL3:
        newLinks.append({"link": "({}, {})".format(0, cn),
                         "delay": linksLatency["({}, {})".format(0, cn)] + higherLatencyCRs[cn]})

    # taking delay between HL1 nodes and HL2+HL3 nodes
    for cn1 in HL1:
        for cn2 in HL2+HL3:
            newLinks.append({"link": "({}, {})".format(cn1, cn2),
                             "delay": linksLatency["({}, {})".format(cn1, cn2)] + higherLatencyCRs[cn2]})

    # taking delay between HL2 nodes and HL3 nodes
    for cn1 in HL2:
        for cn2 in HL3:
            newLinks.append({"link": "({}, {})".format(cn1, cn2),
                             "delay": linksLatency["({}, {})".format(cn1, cn2)] + higherLatencyCRs[cn2]})

    # taking delay between HL1 nodes and HL1 nodes
    for cn1 in HL1:
        for cn2 in HL1:
            if cn1 != cn2:
                if cn1 > cn2:
                    newLinks.append({"link": "({}, {})".format(cn2, cn1),
                                     "delay": linksLatency["({}, {})".format(cn2, cn1)] + higherLatencyCRs[cn1]})
                else:
                    newLinks.append({"link": "({}, {})".format(cn1, cn2),
                                 "delay": linksLatency["({}, {})".format(cn1, cn2)] + higherLatencyCRs[cn2]})

    # taking delay between HL2 nodes and HL2 nodes
    for cn1 in HL2:
        for cn2 in HL2:
            if cn1 != cn2:
                if cn1 > cn2:
                    newLinks.append({"link": "({}, {})".format(cn2, cn1),
                                     "delay": linksLatency["({}, {})".format(cn2, cn1)] + higherLatencyCRs[cn1]})
                else:
                    newLinks.append({"link": "({}, {})".format(cn1, cn2),
                                     "delay": linksLatency["({}, {})".format(cn1, cn2)] + higherLatencyCRs[cn2]})

    # taking delay between HL3 nodes and HL3 nodes
    for cn1 in HL3:
        for cn2 in HL3:
            if cn1 != cn2:
                if cn1 > cn2:
                    newLinks.append({"link": "({}, {})".format(cn2, cn1),
                                     "delay": linksLatency["({}, {})".format(cn2, cn1)] + higherLatencyCRs[cn1]})
                else:
                    newLinks.append({"link": "({}, {})".format(cn1, cn2),
                                     "delay": linksLatency["({}, {})".format(cn1, cn2)] + higherLatencyCRs[cn2]})

    return newLinks


def creatingNewTopoFile(newLinks, newCNs, newE2Ns, q_CRs):
    json.dump({"links": newLinks, "CRs": newCNs, "DUs": newE2Ns}, open("{}_CRs_new_topology.json".format(q_CRs), 'w'))


def newTopoMaker(q_CRs, proportion):
    """
    Creates a new topology based on the nodes position in the base topology.
    q_CRs represents the number of CRs to be generated in the new topology
    """
    baseTopo = topologyFileReader()

    HL1, HL2, HL3 = CRsRandomSelection(proportion)

    # newCNs represents the final list that will be read by the solver/heuristic
    newCNs = creatingNewCRsObj(baseTopo["CRs"], HL1, HL2, HL3)

    linksLatency = AllLinksLatency(baseTopo["links"])
    nextCRs, higherLatencyCRs = E2NodeCRsSelection(baseTopo["DUs"], HL1+HL3+HL3, linksLatency)

    # newE2Ns represents the final list that will be read by the solver/heuristic
    newE2Ns = [{"id": i, "CR": i, "closest_CR": i} for i in HL1+HL2+HL3]

    # newLinks represents the final list that will be read by the solver/heuristic
    newLinks = creatingNewLinks(HL1, HL2, HL3, linksLatency, higherLatencyCRs)

    creatingNewTopoFile(newLinks, newCNs, newE2Ns, q_CRs)


if __name__ == '__main__':
    random.seed(5)
    newTopoMaker(q_CRs=512, proportion=[5, 15, 492])
