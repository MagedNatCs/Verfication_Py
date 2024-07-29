def pre(TS, C, a=None):
    states = C
    result = {t[0] for t in TS["to"] if t[2] in states and (a is None or t[1] == a)}
    return result

def post(TS, C, a=None):
    states = C
    result = {t[2] for t in TS["to"] if t[0] in states and (a is None or t[1] == a)}
    return result

def is_action_deterministic(TS):
    if len(TS["I"]) > 1:
        return False
    for s in TS["S"]:
        for a in TS["Act"]:
            if len(post(TS, s, a)) > 1:
                return False
    return True

def is_label_deterministic(TS):
    if len(TS["I"]) > 1:
        return False
    for s in TS["S"]:
        post_states = post(TS, s)
        seen_labels = []
        for n in post_states:
            label = TS["L"](n)
            if label in seen_labels:
                return False
            seen_labels.append(label)
    return True


TS = {
    "S": {"s1", "s2", "s3"},
    "I": {"s1"},
    "Act": {"a", "b", "c"},
    "to": {("s1", "a", "s2"), ("s1", "a", "s1"), ("s1", "b", "s2"),
          ("s2", "c", "s3"), ("s3", "c", "s1")},
    "AP": {"p", "q"},
    "L": lambda s: {"p"} if s == "s1" else {"p", "q"} if s == "s2" else {}
}

assert post(TS, "s1", "a") == {"s1", "s2"}
print(post(TS, "s1", "a"))
assert post(TS, {"s1", "s2"}, "a") == {"s1", "s2"}
assert pre(TS, {"s1", "s2"}) == {"s1", "s3"}
assert pre(TS, "s1") == {"s1", "s3"}
assert not is_action_deterministic(TS)
assert is_label_deterministic(TS)