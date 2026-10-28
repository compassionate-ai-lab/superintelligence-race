"""M1. Governance-capacity boundary (Chapter 1; also Chapters 5, 19-21).

N   actions per day taken by the system
r   fraction of actions needing human review (sampled + escalated + complaints)
T   review hours per day
k   reviewers;  mu  careful reviews per reviewer-hour
rho utilization = lambda / (k mu), lambda = r N / T  (reviews per hour)
"""
from dataclasses import dataclass


@dataclass
class Oversight:
    N: float
    r: float
    T: float
    k: float
    mu: float

    @property
    def arrival_rate(self):          # reviews per hour
        return self.r * self.N / self.T

    @property
    def capacity(self):              # reviews per hour
        return self.k * self.mu

    @property
    def utilization(self):
        return self.arrival_rate / self.capacity

    def backlog_growth_per_hour(self):
        """Average growth of the review backlog when demand exceeds capacity (0 otherwise)."""
        return max(0.0, self.arrival_rate - self.capacity)

    def n_max(self, rho_target=0.8):
        """Largest daily action volume that can be overseen at the target utilization."""
        return rho_target * self.k * self.mu * self.T / self.r

    def reviewers_needed(self, rho_target=0.8):
        import math
        return math.ceil(self.arrival_rate / (rho_target * self.mu))


def keeps_pace(g_N, g_r, g_k, g_mu):
    """Dynamic condition: growth of N plus growth of r must not exceed growth of k plus growth of mu
    (continuous growth rates per year, e.g. 0.5 for +50%/yr in log terms)."""
    return g_N + g_r <= g_k + g_mu


def worked_example():
    today = Oversight(N=10_000, r=0.07, T=8, k=15, mu=6)
    doubled = Oversight(N=20_000, r=0.07, T=8, k=15, mu=6)
    verified = Oversight(N=20_000, r=0.03, T=8, k=15, mu=6)
    return {
        "lambda_today": today.arrival_rate,
        "rho_today": today.utilization,
        "n_max_today": today.n_max(),
        "backlog_per_hour_doubled": doubled.backlog_growth_per_hour(),
        "backlog_per_day_doubled": doubled.backlog_growth_per_hour() * 8,
        "n_max_r3": verified.n_max(),
        "reviewers_needed_r3": verified.reviewers_needed(),
    }
