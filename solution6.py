from collections import defaultdict

# Transition System Functions
def get_post_states(TS, states):
    if isinstance(states, str):
        states = {states}
    return {transition for transition in TS["to"] if transition[0] in states}

def process_state(state, ts, result_TS, automaton, upholds_condition):
    current_state, automaton_state = state
    post_states = get_post_states(ts, current_state)
    
    for transition in post_states:
        action, next_state = transition[1], transition[2]
        valid_automaton_states = {
            delta[2] for delta in automaton["delta"]
            if delta[0] == automaton_state and upholds_condition(ts["L"](next_state), delta[1])
        }

        for new_automaton_state in valid_automaton_states:
            new_combined_state = (next_state, new_automaton_state)
            new_transition = (state, action, new_combined_state)
            result_TS["to"].add(new_transition)
            if new_combined_state not in result_TS["S"]:
                result_TS["S"].add(new_combined_state)
                process_state(new_combined_state, ts, result_TS, automaton, upholds_condition)

def label_function(state):
    return state[1]

def TS_times_A(ts, automaton, upholds_condition):
    result_TS = defaultdict(set)
    result_TS["Act"] = ts["Act"]
    result_TS["AP"] = automaton["q"]
    result_TS["L"] = label_function
    
    for initial_state in ts['I']:
        for initial_automaton_state in automaton['q0']:
            valid_states = {
                delta[2] for delta in automaton["delta"]
                if delta[0] == initial_automaton_state and upholds_condition(ts["L"](initial_state), delta[1])
            }
            for valid_state in valid_states:
                result_TS["I"].add((initial_state, valid_state))
    
    for initial_combined_state in result_TS['I']:
        result_TS["S"].add(initial_combined_state)
        process_state(initial_combined_state, ts, result_TS, automaton, upholds_condition)
    
    return result_TS

# Generalized NBA to NBA Conversion
def gnba_to_nba(gnba):
    nba = defaultdict(set)
    nba['sigma'] = gnba['sigma']
    num_of_accept_states = len(gnba['f'])

    for i in range(num_of_accept_states):
        for state in gnba['q']:
            nba['q'].add((state, i + 1))

    nba['q0'] = {(initial_state, 1) for initial_state in gnba['q0']}
    nba['f'] = {(state, 1) for state in gnba['f'][0]}

    for i in range(num_of_accept_states):
        current_level = i + 1
        next_level = (i + 2) if (i + 2) <= num_of_accept_states else 1
        
        for transition in gnba['delta']:
            source_state, condition, target_state = transition
            if source_state in gnba['f'][i]:
                nba['delta'].add(((source_state, current_level), condition, (target_state, next_level)))
            else:
                nba['delta'].add(((source_state, current_level), condition, (target_state, current_level)))
    
    return nba
