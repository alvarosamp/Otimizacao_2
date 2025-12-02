from typing import Any, Dict, Iterable, List

from .priority_common import prefix_sums, validate_common_inputs


def mm1_priority_preemptive(
    arrival_rates: Iterable[float],
    mu: float,
) -> Dict[str, Any]:
    """
    Modelo M/M/1 com prioridades preemptivas (com retomada).
    """
    rates = validate_common_inputs(arrival_rates, mu, s=1)
    prefix = prefix_sums(rates)
    total_lambda = prefix[-1]

    if total_lambda == 0:
        return {
            "rho": 0.0,
            "p0": 1.0,
            "L": 0.0,
            "Lq": 0.0,
            "W": 0.0,
            "Wq": 0.0,
            "per_class": [
                {
                    "priority": idx + 1,
                    "lambda": lam,
                    "rho": 0.0,
                    "W": 0.0,
                    "Wq": 0.0,
                    "L": 0.0,
                    "Lq": 0.0,
                }
                for idx, lam in enumerate(rates)
            ],
            "lambda_total": 0.0,
            "service_in_progress": 0.0,
        }

    class_metrics: List[Dict[str, float]] = []
    total_L = 0.0
    total_Lq = 0.0
    for idx, lam in enumerate(rates):
        cum_lambda = prefix[idx]
        prev_lambda = prefix[idx - 1] if idx > 0 else 0.0
        denom_prev = mu - prev_lambda
        denom_cum = mu - cum_lambda
        if denom_prev <= 0 or denom_cum <= 0:
            raise ValueError(
                f"A subfila ate a classe {idx + 1} ficou instavel: lambda={cum_lambda:.6f} >= mu."
            )
        # Formula do gabarito: Wk = (1/mu)/[(1 - sum_prev/mu)*(1 - sum_cum/mu)] = mu / [(mu - prev)(mu - cum)]
        W = mu / (denom_prev * denom_cum)
        Wq = max(W - 1.0 / mu, 0.0)
        L_class = lam * W
        Lq_class = lam * Wq
        total_L += L_class
        total_Lq += Lq_class
        L_cum = cum_lambda * W
        Lq_cum = L_cum - (cum_lambda / mu)
        class_metrics.append(
            {
                "priority": idx + 1,
                "lambda": lam,
                "lambda_cum": cum_lambda,
                "rho": lam / mu,
                "W": W,
                "Wq": Wq,
                # L e Lq exibem os valores do gabarito (cumulativos ate a classe k)
                "L": L_cum,
                "Lq": Lq_cum,
                # Metricas apenas da classe (nao exibidas no gabarito)
                "L_class": L_class,
                "Lq_class": Lq_class,
            }
        )

    rho_total = total_lambda / mu
    if rho_total >= 1:
        raise ValueError("Sistema instavel: lambda_total >= mu.")
    p0 = 1.0 - rho_total
    W_total = total_L / total_lambda if total_lambda > 0 else 0.0
    Wq_total = total_Lq / total_lambda if total_lambda > 0 else 0.0

    return {
        "rho": rho_total,
        "p0": p0,
        "L": total_L,
        "Lq": total_Lq,
        "W": W_total,
        "Wq": Wq_total,
        "per_class": class_metrics,
        "lambda_total": total_lambda,
        "service_in_progress": total_lambda / mu,
    }