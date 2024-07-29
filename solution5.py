# Helper Functions
class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

def initialize_initial_locations_and_actions(pg1, pg2):
    initial_locations = {(l1, l2) for l1 in pg1['Loc0'] for l2 in pg2['Loc0']}
    actions = pg1['Act'] | pg2['Act']
    return initial_locations, actions

def process_transitions_for_pg(current, pg, index, locations, to_check, transitions):
    for (loc, cond, effect, dest) in pg['to']:
        if current[index] == loc:
            new_loc = list(current)
            new_loc[index] = dest
            new_loc = tuple(new_loc)
            transitions.add((current, cond, effect, new_loc))
            if new_loc not in locations:
                locations.add(new_loc)
                to_check.add(new_loc)

def combined_effect_function(pg1, pg2, action, eta):
    if action in pg1['Act']:
        return pg1['Effect'](action, eta)
    else:
        return pg2['Effect'](action, eta)

# Transition Systems Functions
def Lfunction(s, ts1, ts2):
    return ts1['L'](s[0]) | ts2['L'](s[1])

def interleave_transition_systems(ts1, ts2, h):
    I = {(i1, i2) for i1 in ts1['I'] for i2 in ts2['I']}
    S = set(I)
    Act = ts1['Act'] | ts2['Act']
    to = set()
    to_check = set(I)
    
    while to_check:
        current = to_check.pop()
        for (loc1, act1, dest1) in ts1['to']:
            if current[0] == loc1:
                if act1 not in h:
                    new_loc = (dest1, current[1])
                    to.add((current, act1, new_loc))
                    if new_loc not in S:
                        S.add(new_loc)
                        to_check.add(new_loc)
                else:
                    for (loc2, act2, dest2) in ts2['to']:
                        if current[1] == loc2 and act1 == act2:
                            new_loc = (dest1, dest2)
                            to.add((current, act1, new_loc))
                            if new_loc not in S:
                                S.add(new_loc)
                                to_check.add(new_loc)
        for (loc2, act2, dest2) in ts2['to']:
            if current[1] == loc2 and act2 not in h:
                new_loc = (current[0], dest2)
                to.add((current, act2, new_loc))
                if new_loc not in S:
                    S.add(new_loc)
                    to_check.add(new_loc)

    AP = ts1['AP'] | ts2['AP']
    return {
        "S": S,
        "I": I,
        "Act": Act,
        "to": to,
        "AP": AP,
        "L": lambda s: Lfunction(s, ts1, ts2)
    }

# Program Graphs Functions
def interleave_program_graphs(pg1, pg2):
    loc0, Act = initialize_initial_locations_and_actions(pg1, pg2)
    Loc = set(loc0)
    to = set()
    to_check = set(loc0)
    
    while to_check:
        current = to_check.pop()
        process_transitions_for_pg(current, pg1, 0, Loc, to_check, to)
        process_transitions_for_pg(current, pg2, 1, Loc, to_check, to)
    
    Eval = lambda cond, eta: eval(cond, None, eta)
    Effect = lambda action, eta: combined_effect_function(pg1, pg2, action, eta)
    g0 = f'{pg1["g0"]} and {pg2["g0"]}'
    
    return {
        "Loc": Loc,
        "Act": Act,
        "Eval": Eval,
        "Effect": Effect,
        "to": to,
        "Loc0": loc0,
        "g0": g0
    }
