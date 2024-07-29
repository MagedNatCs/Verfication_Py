from abc import ABC, abstractmethod
from typing import Union

#=====================ltl_core(start)==================================================

class LTL(ABC):
    def _sub(self):
        return {self.simplify(), _Not_(self).simplify()}

    @abstractmethod
    def sub(self):
        pass

    def simplify(self):
        return self


class Literal(LTL):

    def __init__(self, x: Union[str, bool, int]):
        super().__init__()
        self.x = x

    def __repr__(self):
        return str(self.x)

    def tex(self):
        return str(self.x)

    def sub(self):
        return self._sub()

    def __eq__(self, other):
        return isinstance(other, Literal) and self.x == other.x or isinstance(other, bool) and self.x == other

    def __hash__(self):
        return hash(self.x)


class Unary(LTL):
    def __init__(self, phi: Union[LTL, str, bool, int], op: str, texop: str):
        super().__init__()
        self.phi = phi if isinstance(phi, LTL) else Literal(phi)
        self.op = op
        self.texop = texop

    def __repr__(self):
        return f'{self.op}({self.phi})'

    def tex(self):
        return f'{self.texop}({self.phi.tex()})'

    def sub(self):
        return self._sub() | self.phi.sub()

    def simplify(self):
        return self.create(self.phi.simplify())

    def __eq__(self, other):
        return isinstance(other, Unary) and self.phi == other.phi and self.op == other.op

    def __hash__(self):
        return hash((self.phi, self.op, self.texop))

    @classmethod
    def create(cls, phi):
        return cls(phi)


class Binary(LTL):
    def __init__(self, phi1: Union[LTL, str, bool, int], phi2: Union[LTL, str], op: str, texop: str):
        super().__init__()
        self.phi1 = phi1 if isinstance(phi1, LTL) else Literal(phi1)
        self.phi2 = phi2 if isinstance(phi2, LTL) else Literal(phi2)
        self.op = op
        self.texop = texop

    def __repr__(self):
        return f'({self.phi1} {self.op} {self.phi2})'

    def tex(self):
        return f'({self.phi1.tex()} {self.texop} {self.phi2.tex()})'

    def sub(self):
        return self._sub() | self.phi1.sub() | self.phi2.sub()

    def simplify(self):
        return self.create(self.phi1.simplify(), self.phi2.simplify())

    def __eq__(self, other):
        return isinstance(other, Binary) and self.phi1 == other.phi1 and self.phi2 == other.phi2 and self.op == other.op

    def __hash__(self):
        return hash((self.phi1, self.phi2, self.op, self.texop))

    @classmethod
    def create(cls, phi1, phi2):
        return cls(phi1, phi2)


class _Not_(Unary):
    def __init__(self, phi):
        super().__init__(phi, 'Not', '\\neg')

    def simplify(self):
        phi = self.phi.simplify()
        if isinstance(phi, _Not_):
            return phi.phi
        return _Not_(phi)

def Not(phi):
    return _Not_(phi).simplify()


class Next(Unary):
    def __init__(self, phi):
        super().__init__(phi, 'O', '\\mathbf{O}')


class Until(Binary):
    def __init__(self, phi1, phi2):
        super().__init__(phi1, phi2, 'U', '\\cup')


class And(Binary):
    def __init__(self, phi1, phi2):
        super().__init__(phi1, phi2, '/\\', '\\land')

#=====================ltl_core(end)==================================================

class Or(Binary):
    def __init__(self, phi1, phi2):
        super().__init__(phi1, phi2, '\/', '\\or')

    def simplify(self):
        return Not(And(Not(self.phi1.simplify()), Not(self.phi2.simplify())))


class Eventually(Unary):
    def __init__(self, phi):
        super().__init__(phi, 'F', '\\_Eventually')

    def simplify(self):
        return Until(True, self.phi.simplify())

class Always(Unary):
    def __init__(self, phi):
        super().__init__(phi, 'G', '\\_Always')

    def simplify(self):
        return Not(Eventually(Not(self.phi.simplify())))

class Implies(Binary):
    def __init__(self, phi1, phi2):
        super().__init__(phi1, phi2, '=>', '\\_Implies')

    def simplify(self):
        return Or(Not(self.phi1.simplify()), self.phi2.simplify()).simplify()

class Release(Binary):
    def __init__(self, phi1, phi2):
        super().__init__(phi1, phi2, 'R', '_Release')

    def simplify(self):
        return Not((Until(Not(self.phi1.simplify()), Not(self.phi2.simplify()))))

def generate_state_space(closure):
    subsets = [[]]
    for exp in closure:
        current = []
        for sub in subsets:
            if Not(exp) not in sub:
                current.append(sub + [exp])
            else:
                current.append(sub)
        subsets += current
    all_subsets = frozenset(frozenset(exp) for exp in subsets)

    all_subsets_true = all_subsets
    maximal_group_size = len(closure)
    if Literal(True) in closure:
        all_subsets_true = set()
        for exp in all_subsets:
            if Literal(True) in exp:
                all_subsets_true.add(exp)
        maximal_group_size += 1
    
    maximal_subsets = set()
    for exp in all_subsets_true:
        if len(exp) == maximal_group_size / 2:
            maximal_subsets.add(exp)

    def is_locally_consistent(B):
        until_exprs = set()
        for exp in closure:
            if isinstance(exp, Until):
                until_exprs.add(exp)
        for phi in until_exprs:
            if not (not (phi.phi2 in B) or (phi in B)):
                return False
            if not (not ((phi in B) and (phi.phi2 not in B)) or (phi.phi1 in B)):
                return False
        return True

    def is_logically_consistent(B):
        and_exprs = set()
        for exp in closure:
            if isinstance(exp, And):
                and_exprs.add(exp)
        for phi in and_exprs:
            if not ((not phi in B) or ((phi.phi1 in B) and (phi.phi2 in B))):
                return False
            if not ((not phi.phi1 in B) or (not phi.phi2 in B) or (phi in B)):
                return False
        return True
    result = set()
    for sub in maximal_subsets:
        if (is_locally_consistent(sub) and is_logically_consistent(sub)):
            result.add(sub)
    return result

def initial_states(phi, Q):
    result = set()
    for B in Q:
        if phi in B:
            result.add(B)
    return result


def accepting_states(closure, Q):
    result = frozenset()
    for exp in closure:
        if isinstance(exp, Until):
            bi = {frozenset(filter(lambda B: (exp not in B) or (exp.phi2 in B), Q))}
            result = result | bi
    return result

def transition_relation(closure, Q):
    result = set()
    for B in Q:
        A = set()
        for a in (B.difference({Literal(True)})):
            if isinstance(a, Literal):
                A.add(a)
        to_set = set()
        for B_tag in Q:
            condition1 = True
            for phi in closure:
                if isinstance(phi, Next):
                    if not ((phi not in B) or (phi.phi in B_tag)):
                        condition1 = False
                        break
                    if not ((phi.phi not in B_tag) or (phi in B)):
                        condition1 = False
                        break
            if not condition1:
                continue
            
            condition2 = True
            for phi in closure:
                if isinstance(phi, Until):
                    if not (not ((phi in B) and (phi.phi2 not in B)) or (phi in B_tag)):
                        condition2 = False
                        break
                    if not (not ((phi not in B) and (phi.phi1 in B)) or (phi not in B_tag)):
                        condition2 = False
                        break
            if not condition2:
                continue
            to_set.add(B_tag)
        result = result | frozenset([(B, frozenset(A), B_tag) for B_tag in to_set])
    return result


def atomic_propositions(closure):
    literals = [phi for phi in closure if isinstance(phi, Literal) and phi != Literal(True)]
    result = [[]]
    for exp in literals:
        curr = []
        for sub in result:
            curr.append(sub + [exp])
        result += curr
    return frozenset(frozenset(exp) for exp in result)


def ltl_to_gnba(phi):
    gnba = {}
    closure = phi.simplify().sub() - {Not(True)}
    q = generate_state_space(closure)
    gnba['q'] = q
    gnba['q0'] = initial_states(phi, q)
    gnba['f'] = accepting_states(closure, q)
    gnba['delta'] = transition_relation(closure, q)
    gnba['sigma'] = atomic_propositions(closure)

    return gnba
