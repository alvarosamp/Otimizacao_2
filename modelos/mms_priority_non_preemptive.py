from typing import Any, Dict, Iterable, List

from math import factorial

from .mms_priority_preemptive import mms_priority_preemptive
from .priority_common import aggregate_totals, prefix_sums, validate_common_inputs
from .mm1_priority_non_preemptive import mm1_priority_non_preemptive


def mms_priority_non_preemptive(
    arrival_rates: Iterable[float],
    mu: float,
    s: int,
) -> Dict[str, Any]:
    """
    Modelo M/M/s com prioridades nao preemptivas.
    """
    if s == 1:
        # Caso especial com um unico servidor: usar o modelo dedicado S=1.
        return mm1_priority_non_preemptive(arrival_rates, mu)

    rates = validate_common_inputs(arrival_rates, mu, s=s)
    prefix = prefix_sums(rates)
    total_lambda = prefix[-1]

    if total_lambda == 0:
        return mms_priority_preemptive(arrival_rates, mu, s)

    # Formula do gabarito para s > 1 (sem interrupcao).
    r = total_lambda / mu
    sum_terms = sum((r**j) / factorial(j) for j in range(s))
    if r == 0:
        base_factor = s * mu
    else:
        base_factor = (factorial(s) * (s * mu - total_lambda) / (r**s)) * sum_terms + (s * mu)

    class_metrics: List[Dict[str, float]] = []
    for idx, lam in enumerate(rates):
        prev_lambda = prefix[idx - 1] if idx > 0 else 0.0
        cum_lambda = prefix[idx]

        factor_prev = 1.0 - (prev_lambda / (s * mu))
        factor_cum = 1.0 - (cum_lambda / (s * mu))
        if factor_prev <= 0 or factor_cum <= 0:
            raise ValueError(
                f"A subfila ate a classe {idx + 1} ficou instavel: lambda={cum_lambda:.6f} >= s*mu."
            )

        W = (1.0 / (base_factor * factor_prev * factor_cum)) + (1.0 / mu)
        Wq = max(W - 1.0 / mu, 0.0)
        L = lam * W
        Lq = max(L - (lam / mu), 0.0)

        class_metrics.append(
            {
                "priority": idx + 1,
                "lambda": lam,
                "rho": lam / (s * mu),
                "W": W,
                "Wq": Wq,
                "L": L,
                "Lq": Lq,
                "base_factor": base_factor,
            }
        )

    return aggregate_totals(class_metrics, mu=mu, s=s)