from typing import Any, Dict, Iterable, List

from .mm1_priority_preemptive import mm1_priority_preemptive
from .priority_common import aggregate_totals, prefix_sums, validate_common_inputs


def mm1_priority_non_preemptive(
    arrival_rates: Iterable[float],
    mu: float,
) -> Dict[str, Any]:
    """
    Modelo M/M/1 com prioridades nao preemptivas.
    """
    rates = validate_common_inputs(arrival_rates, mu, s=1)
    prefix = prefix_sums(rates)
    total_lambda = prefix[-1]

    if total_lambda == 0:
        return mm1_priority_preemptive(arrival_rates, mu)

    class_metrics: List[Dict[str, float]] = []
    for idx, lam in enumerate(rates):
        cum_lambda = prefix[idx]
        higher_lambda = prefix[idx - 1] if idx > 0 else 0.0
        denom_cum = mu - cum_lambda
        denom_prev = mu - higher_lambda
        if denom_cum <= 0 or denom_prev <= 0:
            raise ValueError(
                f"A subfila ate a classe {idx + 1} ficou instavel: lambda={cum_lambda:.6f} >= mu."
            )
        # Formula ajustada ao gabarito: Wq_k = lambda_total / [(mu - lambda_{1..k-1})(mu - lambda_{1..k})]
        Wq = total_lambda / (denom_prev * denom_cum)
        W = Wq + 1.0 / mu
        Lq = lam * Wq
        L = lam * W
        class_metrics.append(
            {
                "priority": idx + 1,
                "lambda": lam,
                "rho": lam / mu,
                "W": W,
                "Wq": Wq,
                "L": L,
                "Lq": Lq,
            }
        )

    return aggregate_totals(class_metrics, mu=mu, s=1)