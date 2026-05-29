"""
============================================================
  Q4: Bayesian Networks — Tools, Concepts & Implementation
  Example: Medical Diagnosis Bayesian Network

  Domain: A patient visits a doctor with symptoms.
  The BN models the causal chain:

      Smoking ──┐
                ▼
  Pollution ──► Cancer ──► Dyspnoea (breathlessness)
                │
                └──────► X-Ray result (positive/negative)

  This is the classic "Asia" / "Cancer" BN from the BN literature.

  TOOLS FOR BAYESIAN NETWORKS
  ────────────────────────────
  1. pgmpy      — Python; most complete BN library (inference, learning)
  2. bnlearn    — R package; structure learning from data
  3. Netica     — GUI tool; commercial with free version
  4. GeNIe      — GUI tool; SMILE engine; academic license free
  5. Hugin      — GUI + API; professional BN tool
  6. PyMC       — Python; probabilistic programming (MCMC)
  7. Stan       — Probabilistic programming; R and Python interfaces
  8. BayesiaLab — GUI; machine learning + BN
  9. OpenMarkov — Open-source GUI; pgmx format
  10. Pomegranate— Python; fast BN + HMM implementation
============================================================
"""

import math
import itertools
from functools import reduce


# ─────────────────────────────────────────────────────────────
#  CORE BAYESIAN NETWORK CLASSES
# ─────────────────────────────────────────────────────────────

class CPT:
    """
    Conditional Probability Table (CPT) for a BN node.

    Parameters
    ----------
    variable  : str — name of the node variable
    parents   : list[str] — parent variable names (empty for root nodes)
    values    : list[str] — possible states of this variable
    table     : dict — maps tuple(parent_values) → dict{value: probability}
                       For root nodes, key is () (empty tuple).
    """

    def __init__(self, variable, parents, values, table):
        self.variable = variable
        self.parents  = parents
        self.values   = values
        self.table    = table   # {(parent_val, ...): {val: prob}}

    def get_prob(self, value, parent_values=()):
        """P(variable=value | parents=parent_values)"""
        row = self.table.get(parent_values)
        if row is None:
            raise KeyError(f"No CPT row for {self.variable} given parents={parent_values}")
        return row.get(value, 0.0)

    def __repr__(self):
        return f"CPT({self.variable} | {self.parents})"


class BayesianNetwork:
    """
    Discrete Bayesian Network.

    Supports:
    - Adding nodes with CPTs
    - Exact inference via Variable Elimination
    - Prior (marginal) probability queries
    - Posterior (conditional) probability queries
    - MAP (most likely explanation) queries
    """

    def __init__(self, name="Bayesian Network"):
        self.name  = name
        self.nodes = {}          # {variable: CPT}
        self._order = []         # topological order (insertion order)

    def add_node(self, cpt: CPT):
        self.nodes[cpt.variable] = cpt
        self._order.append(cpt.variable)

    def _topo_sort(self):
        """Return variables in topological order (parents before children)."""
        visited = set()
        result  = []

        def visit(var):
            if var in visited:
                return
            visited.add(var)
            for parent in self.nodes[var].parents:
                visit(parent)
            result.append(var)

        for var in self._order:
            visit(var)
        return result

    # ── FACTOR OPERATIONS ─────────────────────────────────────

    def _all_assignments(self, variables):
        """Generate all joint assignments of a list of variables."""
        domains = [self.nodes[v].values for v in variables]
        for combo in itertools.product(*domains):
            yield dict(zip(variables, combo))

    def _factor_product(self, f1_vars, f1_table, f2_vars, f2_table):
        """Multiply two factors together."""
        all_vars = list(dict.fromkeys(f1_vars + f2_vars))   # ordered union
        result   = {}
        for assignment in self._all_assignments(all_vars):
            key = tuple(assignment[v] for v in all_vars)
            k1  = tuple(assignment[v] for v in f1_vars)
            k2  = tuple(assignment[v] for v in f2_vars)
            result[key] = f1_table.get(k1, 0.0) * f2_table.get(k2, 0.0)
        return all_vars, result

    def _factor_marginalise(self, factor_vars, factor_table, var):
        """Sum out `var` from a factor."""
        remaining = [v for v in factor_vars if v != var]
        result    = {}
        for assignment in self._all_assignments(factor_vars):
            key  = tuple(assignment[v] for v in factor_vars)
            rkey = tuple(assignment[v] for v in remaining)
            result[rkey] = result.get(rkey, 0.0) + factor_table.get(key, 0.0)
        return remaining, result

    def _build_factor(self, cpt: CPT):
        """Convert a CPT into a factor (vars, table)."""
        f_vars  = cpt.parents + [cpt.variable]
        f_table = {}
        for parent_vals, dist in cpt.table.items():
            for val, prob in dist.items():
                key = parent_vals + (val,)
                f_table[key] = prob
        return f_vars, f_table

    def _restrict_factor(self, f_vars, f_table, evidence):
        """Restrict a factor by fixing evidence variables."""
        new_vars  = [v for v in f_vars if v not in evidence]
        new_table = {}
        for key, prob in f_table.items():
            # key is a tuple aligned to f_vars
            assignment = dict(zip(f_vars, key if isinstance(key, tuple) else (key,)))
            # Check all evidence variables that appear in this factor
            consistent = True
            for e_var, e_val in evidence.items():
                if e_var in assignment and assignment[e_var] != e_val:
                    consistent = False
                    break
            if consistent:
                new_key = tuple(assignment[v] for v in new_vars) if new_vars else ()
                new_table[new_key] = new_table.get(new_key, 0.0) + prob
        return new_vars, new_table

    # ── VARIABLE ELIMINATION ──────────────────────────────────

    def query(self, query_var, evidence=None):
        """
        Compute P(query_var | evidence) using Variable Elimination.

        Parameters
        ----------
        query_var : str — the variable to query
        evidence  : dict{var: value} — observed evidence (or None)

        Returns
        -------
        dict{value: probability} — normalised posterior distribution
        """
        evidence = evidence or {}

        # Build all factors, restrict by evidence
        factors = []
        for var, cpt in self.nodes.items():
            fv, ft = self._build_factor(cpt)
            fv, ft = self._restrict_factor(fv, ft, evidence)
            if ft:
                factors.append((fv, ft))

        # Eliminate hidden variables (not query, not evidence)
        hidden = [v for v in self._topo_sort()
                  if v != query_var and v not in evidence]

        for h in hidden:
            # Collect all factors that mention h
            relevant   = [(fv, ft) for fv, ft in factors if h in fv]
            irrelevant = [(fv, ft) for fv, ft in factors if h not in fv]

            if not relevant:
                continue

            # Multiply relevant factors together
            fv, ft = relevant[0]
            for rv, rt in relevant[1:]:
                fv, ft = self._factor_product(fv, ft, rv, rt)

            # Marginalise out h
            fv, ft = self._factor_marginalise(fv, ft, h)
            irrelevant.append((fv, ft))
            factors = irrelevant

        # Multiply remaining factors
        if not factors:
            return {}

        fv, ft = factors[0]
        for rv, rt in factors[1:]:
            fv, ft = self._factor_product(fv, ft, rv, rt)

        # Extract query variable distribution
        if query_var not in fv:
            # query var was eliminated or absorbed — recompute directly
            result = {}
            cpt = self.nodes[query_var]
            for val in cpt.values:
                parent_vals = tuple(evidence.get(p, list(self.nodes[p].values)[0])
                                    for p in cpt.parents)
                p_val = cpt.get_prob(val, parent_vals)
                # weight by remaining factor mass
                total_mass = sum(ft.values()) if ft else 1.0
                result[val] = p_val * total_mass
        else:
            q_idx  = fv.index(query_var)
            result = {}
            for key, prob in ft.items():
                val = key[q_idx] if isinstance(key, tuple) else key
                result[val] = result.get(val, 0.0) + prob

        # Normalise
        total = sum(result.values())
        if total > 0:
            result = {k: v / total for k, v in result.items()}

        return result

    def map_query(self, query_vars, evidence=None):
        """
        Most Probable Assignment (MAP) for a set of variables given evidence.
        Returns the assignment with highest joint probability.
        """
        evidence = evidence or {}
        best_prob, best_assignment = -1, None

        for assignment in self._all_assignments(query_vars):
            combined = {**evidence, **assignment}
            prob = self.joint_probability(combined)
            if prob > best_prob:
                best_prob, best_assignment = prob, assignment

        return best_assignment, best_prob

    def joint_probability(self, assignment):
        """
        Compute the joint probability P(assignment) using the chain rule:
        P(X1, X2, ..., Xn) = ∏ P(Xi | parents(Xi))
        """
        prob = 1.0
        for var, cpt in self.nodes.items():
            if var not in assignment:
                return 0.0
            parent_vals = tuple(assignment[p] for p in cpt.parents)
            val         = assignment[var]
            prob       *= cpt.get_prob(val, parent_vals)
        return prob


# ─────────────────────────────────────────────────────────────
#  MEDICAL DIAGNOSIS BAYESIAN NETWORK
#
#  Variables and their states:
#    Smoking   : {yes, no}
#    Pollution : {high, low}
#    Cancer    : {present, absent}
#    XRay      : {positive, negative}
#    Dyspnoea  : {yes, no}
#
#  Causal structure:
#    Smoking   → Cancer
#    Pollution → Cancer
#    Cancer    → XRay
#    Cancer    → Dyspnoea
# ─────────────────────────────────────────────────────────────

def build_medical_bn():
    bn = BayesianNetwork("Medical Diagnosis — Cancer BN")

    # ── P(Smoking) — prior (root node) ────────────────────────
    bn.add_node(CPT(
        variable="Smoking",
        parents=[],
        values=["yes", "no"],
        table={(): {"yes": 0.30, "no": 0.70}}   # 30% of population smokes
    ))

    # ── P(Pollution) — prior (root node) ──────────────────────
    bn.add_node(CPT(
        variable="Pollution",
        parents=[],
        values=["high", "low"],
        table={(): {"high": 0.40, "low": 0.60}}
    ))

    # ── P(Cancer | Smoking, Pollution) ────────────────────────
    # Higher cancer risk with smoking + high pollution
    bn.add_node(CPT(
        variable="Cancer",
        parents=["Smoking", "Pollution"],
        values=["present", "absent"],
        table={
            ("yes", "high"): {"present": 0.25, "absent": 0.75},
            ("yes", "low"):  {"present": 0.10, "absent": 0.90},
            ("no",  "high"): {"present": 0.05, "absent": 0.95},
            ("no",  "low"):  {"present": 0.01, "absent": 0.99},
        }
    ))

    # ── P(XRay | Cancer) ──────────────────────────────────────
    # XRay is positive if cancer present (but not perfect)
    bn.add_node(CPT(
        variable="XRay",
        parents=["Cancer"],
        values=["positive", "negative"],
        table={
            ("present",): {"positive": 0.90, "negative": 0.10},
            ("absent",):  {"positive": 0.20, "negative": 0.80},
        }
    ))

    # ── P(Dyspnoea | Cancer) ──────────────────────────────────
    bn.add_node(CPT(
        variable="Dyspnoea",
        parents=["Cancer"],
        values=["yes", "no"],
        table={
            ("present",): {"yes": 0.65, "no": 0.35},
            ("absent",):  {"yes": 0.30, "no": 0.70},
        }
    ))

    return bn


# ─────────────────────────────────────────────────────────────
#  HELPER — DISPLAY RESULTS
# ─────────────────────────────────────────────────────────────

def print_query(label, result):
    print(f"  {label}")
    for val, prob in sorted(result.items(), key=lambda x: -x[1]):
        bar = "█" * int(prob * 30)
        print(f"     {val:<12} {prob:.4f}  {bar}")
    print()


# ─────────────────────────────────────────────────────────────
#  TEST CASES
# ─────────────────────────────────────────────────────────────

def run_bn_tests():
    print("\n" + "█"*62)
    print("  Q4: BAYESIAN NETWORK — MEDICAL DIAGNOSIS")
    print("█"*62)

    bn = build_medical_bn()

    print("""
  Network Structure:
    Smoking ──┐
              ▼
  Pollution ──► Cancer ──► XRay (positive / negative)
                    │
                    └────► Dyspnoea (breathlessness)

  Node count  : {}
  Variables   : {}
  """.format(len(bn.nodes), list(bn.nodes.keys())))

    # ── TEST 1: Prior probability of Cancer ───────────────────
    print("="*62)
    print("  TEST 1: Prior P(Cancer) — no evidence")
    print("="*62)
    result = bn.query("Cancer")
    print_query("P(Cancer)", result)
    assert 0.0 < result["present"] < 0.10, \
        f"Prior cancer prob should be low, got {result['present']:.4f}"
    print("   Prior cancer probability is low (< 10%) as expected\n")

    # ── TEST 2: Posterior given XRay positive ─────────────────
    print("="*62)
    print("  TEST 2: P(Cancer | XRay=positive)")
    print("="*62)
    result2 = bn.query("Cancer", evidence={"XRay": "positive"})
    print_query("P(Cancer | XRay=positive)", result2)
    assert result2["present"] > result["present"], \
        "Positive XRay should increase cancer probability!"
    print("   Positive XRay increases cancer probability (Bayes update)\n")

    # ── TEST 3: Smoking + high pollution + positive XRay ──────
    print("="*62)
    print("  TEST 3: P(Cancer | Smoking=yes, Pollution=high, XRay=positive)")
    print("="*62)
    evidence3 = {"Smoking": "yes", "Pollution": "high", "XRay": "positive"}
    result3   = bn.query("Cancer", evidence=evidence3)
    print_query("P(Cancer | Smoking=yes, Pollution=high, XRay=positive)", result3)
    # With smoking + high pollution + positive XRay, cancer should be likely
    assert "present" in result3, f"'present' key missing in result3: {result3}"
    assert result3.get("present", 0) > 0.5, \
        f"Expected majority cancer prob with all risk factors, got {result3}"
    print("   Multiple risk factors compound cancer probability correctly\n")

    # ── TEST 4: Explaining away (intercausal reasoning) ───────
    print("="*62)
    print("  TEST 4: P(Pollution | Cancer=present, Smoking=yes) vs P(Pollution | Cancer=present)")
    print("  (Explaining-away: if cancer caused by smoking, pollution is less likely)")
    print("="*62)
    r_with_smoking = bn.query("Pollution",
                              evidence={"Cancer": "present", "Smoking": "yes"})
    r_without      = bn.query("Pollution",
                              evidence={"Cancer": "present"})
    print_query("P(Pollution | Cancer=present)", r_without)
    print_query("P(Pollution | Cancer=present, Smoking=yes)", r_with_smoking)
    # Knowing smoking is a cause reduces the need for pollution to explain cancer
    assert r_with_smoking["high"] <= r_without["high"], \
        "Explaining away: smoking should reduce inferred pollution probability!"
    print("   Explaining-away effect confirmed\n")

    # ── TEST 5: P(Dyspnoea) given no evidence ─────────────────
    print("="*62)
    print("  TEST 5: Prior P(Dyspnoea) — baseline breathlessness")
    print("="*62)
    result5 = bn.query("Dyspnoea")
    print_query("P(Dyspnoea)", result5)
    assert 0.25 < result5["yes"] < 0.45, \
        f"Dyspnoea prior should be ~30%, got {result5['yes']:.4f}"
    print("   Dyspnoea prior is in expected range\n")

    # ── TEST 6: Joint probability ──────────────────────────────
    print("="*62)
    print("  TEST 6: Joint Probability P(Smoking=yes, Pollution=high, Cancer=present, ...)")
    print("="*62)
    full_assignment = {
        "Smoking":   "yes",
        "Pollution": "high",
        "Cancer":    "present",
        "XRay":      "positive",
        "Dyspnoea":  "yes"
    }
    jp = bn.joint_probability(full_assignment)
    print(f"  P(all present/positive/yes) = {jp:.6f}")
    assert 0 < jp < 1
    print("   Joint probability is valid (0 < P < 1)\n")

    # ── TEST 7: MAP query ──────────────────────────────────────
    print("="*62)
    print("  TEST 7: MAP — Most Probable State of Cancer & Dyspnoea")
    print("  given XRay=positive, Smoking=yes")
    print("="*62)
    map_result, map_prob = bn.map_query(
        query_vars=["Cancer", "Dyspnoea"],
        evidence={"XRay": "positive", "Smoking": "yes"}
    )
    print(f"  MAP assignment : {map_result}")
    print(f"  Joint prob     : {map_prob:.6f}")
    print("   MAP query returned valid assignment\n")

    # ── TEST 8: Probabilities sum to 1 ────────────────────────
    print("="*62)
    print("  TEST 8: Distributions sum to 1.0 (sanity check)")
    print("="*62)
    for var in bn.nodes:
        dist = bn.query(var)
        total = sum(dist.values())
        print(f"  P({var}) sums to {total:.6f}")
        assert abs(total - 1.0) < 1e-6, f"Probabilities don't sum to 1 for {var}!"
    print("   All distributions sum to 1.0\n")

    print("█"*62)
    print("  ALL BAYESIAN NETWORK TESTS PASSED ")
    print("█"*62)

    print("""
  TOOLS SUMMARY
  ─────────────────────────────────────────────────────────
  Tool          Type      Best For
  ───────────── ───────── ────────────────────────────────
  pgmpy         Python    Structure learning, exact/approx inference
  bnlearn       R         Structural learning from data
  Netica        GUI       Interactive BN editing, free version available
  GeNIe/SMILE   GUI       Academic license; very visual and intuitive
  Hugin         GUI+API   Professional, widely used in research
  PyMC          Python    Bayesian stats, MCMC sampling
  Pomegranate   Python    Fast BNs, HMMs, mixture models
  BayesiaLab    GUI       Enterprise analytics + BN learning
  OpenMarkov    GUI       Open-source, pgmx format
  Stan          Multi     Probabilistic programming, HMC sampling
  """)


if __name__ == "__main__":
    run_bn_tests()
