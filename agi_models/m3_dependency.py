"""M3. Dependencies and collective failure (Chapters 5, 10, 13, 14, 22).

Sequential success: P(all n steps succeed) = prod P(S_i | earlier) ; equals p**n only
under equal conditional success.
Common-cause failure (beta-factor model): two checks each fail with probability q;
a fraction beta of failures share one cause, so
    P(both fail) = beta*q + ((1-beta)*q)**2
Independence (beta = 0) gives q**2.
"""
from functools import reduce


def chain_success(conditional_probs):
    return reduce(lambda a, b: a * b, conditional_probs, 1.0)


def both_checks_fail(q, beta):
    return beta * q + ((1 - beta) * q) ** 2


def reachable(graph, start):
    """Nodes reachable from start in a directed authority/dependency graph {node: [nodes]}."""
    seen, stack = set(), [start]
    while stack:
        n = stack.pop()
        for m in graph.get(n, []):
            if m not in seen:
                seen.add(m); stack.append(m)
    return seen


def worked_example():
    hospital = {   # who can act on what, February 2032 (Chapter 20)
        "supplier_interface": ["agent"],
        "agent": ["bookings_H1", "bookings_H2", "bookings_H3"],
        "ward_lead_H1": ["agent@H1"], "ward_lead_H2": ["agent@H2"], "ward_lead_H3": ["agent@H3"],
    }
    return {
        "chain_20_steps_098": chain_success([0.98] * 20),
        "two_checks_independent": both_checks_fail(0.05, 0.0),
        "two_checks_beta_0.2": both_checks_fail(0.05, 0.2),
        "blast_radius_supplier_change": sorted(reachable(hospital, "supplier_interface")),
    }
