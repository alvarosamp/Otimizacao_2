from typing import Any, Dict, Iterable, List

from .mms import mms
from .priority_common import erlang_c, prefix_sums, validate_common_inputs
from .mm1_priority_preemptive import mm1_priority_preemptive


def mms_priority_preemptive(
    arrival_rates: Iterable[float],
    mu: float,
    s: int,
) -> Dict[str, Any]:
    """
    Modelo M/M/s com prioridades preemptivas.
    Para s=1 usa as formulas dedicadas; para s>=2 usa a media ponderada do M/M/s agregado
    para obter Wk (bate com o gabarito de S=2).
    """
    if s == 1:
        return mm1_priority_preemptive(arrival_rates, mu)

    rates = validate_common_inputs(arrival_rates, mu, s=s)
    prefix = prefix_sums(rates)

    total_lambda = prefix[-1]
    if total_lambda == 0:
        zero_metrics = [
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
        ]
        return {
            "rho": 0.0,
            "p0": 1.0,
            "L": 0.0,
            "Lq": 0.0,
            "W": 0.0,
            "Wq": 0.0,
            "per_class": zero_metrics,
            "lambda_total": 0.0,
            "service_in_progress": 0.0,
        }

    totals_mms = mms(total_lambda, mu, s)
    total_W = totals_mms["W"]
    total_Wq = totals_mms["Wq"]
    total_L = totals_mms["L"]
    total_Lq = totals_mms["Lq"]
    p0 = totals_mms["p0"]

    class_metrics: List[Dict[str, float]] = []
    W_list: List[float] = []

    for idx, lam in enumerate(rates):
        cum_lambda = prefix[idx]
        erlang_c_value = erlang_c(cum_lambda, mu, s)

        # Wbar para subfila 1..k via M/M/s agregado
        mms_cum = mms(cum_lambda, mu, s)
        Wbar_cum = mms_cum["W"]

        if idx == 0:
            Wk = Wbar_cum
        else:
            numer = cum_lambda * Wbar_cum
            for j in range(idx):
                numer -= rates[j] * W_list[j]
            Wk = numer / lam

        Wqk = max(Wk - 1.0 / mu, 0.0)
        L_cum = cum_lambda * Wk
        Lq_cum = max(L_cum - (cum_lambda / mu), 0.0)
        L_class = lam * Wk
        Lq_class = lam * Wqk
        W_list.append(Wk)

        class_metrics.append(
            {
                "priority": idx + 1,
                "lambda": lam,
                "lambda_cum": cum_lambda,
                "rho": lam / (s * mu),
                "W": Wk,
                "Wq": Wqk,
                "L": L_cum,
                "Lq": Lq_cum,
                "L_class": L_class,
                "Lq_class": Lq_class,
                "P(wait)": erlang_c_value,
            }
        )

    return {
        "rho": total_lambda / (s * mu),
        "p0": p0,
        "L": total_L,
        "Lq": total_Lq,
        "W": total_W,
        "Wq": total_Wq,
        "per_class": class_metrics,
        "lambda_total": total_lambda,
        "service_in_progress": total_lambda / mu,
    }