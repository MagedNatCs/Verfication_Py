class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

def get_all_possible_evals(vars):
    evals = set()
    current_eval = HashableDict()
    evals_helper(evals, current_eval, vars.copy())
    return evals

def evals_helper(accumulator, current_eval, vars):
    if vars:
        var, var_range = vars.popitem()
        for value in var_range:
            new_eval = HashableDict({var: value})
            evals_helper(accumulator, HashableDict({**current_eval, **new_eval}), vars.copy())
    else:
        accumulator.add(current_eval)

def labeling_function(state, labels, program_graph):
    result = {state[0]}
    eta = state[1]
    for label in labels:
        if program_graph['Eval'](label, eta):
            result.add(label)
    return result

def transition_system_from_program_graph(program_graph, vars, labels):
    all_evals = get_all_possible_evals(vars)
    states = set()
    initial_states = set()
    actions = program_graph['Act']
    transitions = set()
    atomic_propositions = labels.union(program_graph['Loc'])
    label_function = lambda s: labeling_function(s, labels, program_graph)

    # Initial states
    initial_guard = program_graph['g0']
    for initial_location in program_graph['Loc0']:
        for eval_ in all_evals:
            if program_graph['Eval'](initial_guard, eval_):
                initial_states.add((initial_location, eval_))

    # States and transitions
    to_check = initial_states.copy()
    while to_check:
        current_state = to_check.pop()
        states.add(current_state)
        current_location, current_eta = current_state
        for (from_loc, guard, action, to_loc) in program_graph['to']:
            if current_location == from_loc and program_graph['Eval'](guard, current_eta):
                next_eta = HashableDict(program_graph['Effect'](action, current_eta))
                next_state = (to_loc, next_eta)
                if next_state not in states:
                    to_check.add(next_state)
                transitions.add((current_state, action, next_state))

    return {
        "S": states,
        "I": initial_states,
        "Act": actions,
        "to": transitions,
        "AP": atomic_propositions,
        "L": label_function
    }
