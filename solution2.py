import networkx as nx


import networkx as nx

def generate_graph(ts):
    graph = nx.MultiDiGraph()
    for from_state, action, to_state in ts["to"]:
        graph.add_edge(from_state, to_state, weight=action)
    return graph

def property0(ts):
    word1 = "crit1"
    word2 = "crit2"
    if word1 not in ts["AP"] or word2 not in ts["AP"]:
        return False
    
    for from_state, action, to_state in ts["to"]:
        labels_from = ts["L"](from_state)
        labels_to = ts["L"](to_state)
        
        if (word1 in labels_from and word2 in labels_from) or (word1 in labels_to and word2 in labels_to):
            return True

    return False

def property1(ts):
    word1 = "even"
    word2 = "prime"
    if word1 not in ts["AP"] or (word1 in ts["AP"] and word2 not in ts["AP"]):
        return True
    
    for from_state, action, to_state in ts["to"]:
        labels_from = ts["L"](from_state)
        labels_to = ts["L"](to_state)
        
        if word1 in labels_from and word2 in labels_to:
            return False

    return True

def property2(ts):
    word = "tick"
    connectivity_info = {state: [False, False] for state in ts["S"]}
    
    for from_state, action, to_state in ts["to"]:
        connectivity_info[from_state][0] = True
        connectivity_info[to_state][1] = True
    
    for info in connectivity_info.values():
        if not all(info):
            return False
    
    tick_states = [state for state in ts["S"] if word in ts["L"](state)]
    
    for tick_state in tick_states:
        if not any(tick_state == to_state for from_state, action, to_state in ts["to"]):
            return False

    return True



TS1 = {
    "S": {"s1", "s2", "s3"},
    "I": {"s1"},
    "Act": {"a", "b"},
    "to": {("s1", "a", "s1"), ("s1", "b", "s2"), ("s1", "a", "s2"),
           ("s1", "a", "s3"), ("s3", "a", "s1")},
    "AP": {"crit1", "even", "prime", "tick", "crit2"},
    "L": lambda s: {"crit1", "even", "prime", "tick"} if s == "s1" else {"crit1", "crit2"} if s == "s3" else {}
}

TS2 = {
    "S": {"s1", "s2", "s3", "s4"},
    "I": {"s1"},
    "Act": {"a"},
    "to": {("s1", "a", "s1"), ("s1", "a", "s2"), ("s2", "a", "s1"),
           ("s2", "a", "s4"), ("s2", "a", "s3"), ("s3", "a", "s1"),
           ("s3", "a", "s4"), ("s4", "a", "s3"), ("s4", "a", "s2")},
    "AP": {"crit1", "even", "prime", "tick", "crit2"},
    "L": lambda s: {"prime", "tick"} if s == "s1" else {"crit2"} if s == "s2" else {"crit1"} if s == "s3" else {"tick",
                                                                                                                "even"}
}


def runTests():
    assert property0(TS1)
    assert not property0(TS2)
    assert not property1(TS1)
    assert property1(TS2)
    assert not property2(TS1)
    assert property2(TS2)
    print("All good!")


if __name__ == '__main__':
    runTests()