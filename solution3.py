import itertools

def transition_system_from_circuit(numberOfInputs, numberOfRegisters, numberOfOutputs, updateRegisters, computeOutputs):
    TS = {}

    # generate all possible states
    boolean_values = [False, True]
    TS["S"] = set(itertools.product(boolean_values, repeat=numberOfInputs + numberOfRegisters))

    # generate all possible actions
    TS["Act"] = set(itertools.product(boolean_values, repeat=numberOfInputs))

    # initial states
    TS["I"] = set((False,) * numberOfRegisters + act for act in TS["Act"])

    # transitions
    TS["to"] = set()
    for state in TS["S"]:
        for act in TS["Act"]:
            new_registers = updateRegisters(state) + act
            TS["to"].add((state, act, new_registers))

    # atomic propositions
    TS["AP"] = set(
        ["x" + str(i) for i in range(1, numberOfInputs + 1)] +
        ["r" + str(i) for i in range(1, numberOfRegisters + 1)] +
        ["y" + str(i) for i in range(1, numberOfOutputs + 1)]
    )

    # labeling function
    def labeling_function(state):
        labels = set()
        for ap in TS["AP"]:
            index = int(ap[1:]) - 1
            if ap[0] == "x" and state[index + numberOfRegisters]:
                labels.add(ap)
            elif ap[0] == "r" and state[index]:
                labels.add(ap)
            elif ap[0] == "y" and computeOutputs(state)[index]:
                labels.add(ap)
        return labels

    TS["L"] = labeling_function

    return TS
