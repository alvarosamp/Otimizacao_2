from math import factorial
from typing import Any, Dict, Iterable, List


def coerce_arrival_rates(arrival_rates: Iterable[float]) -> List[float]:
    if arrival_rates is None:
        raise ValueError("E necessario fornecer as taxas de chegada por prioridade.")

    try:
        rates = [float(value) for value in arrival_rates]
    except TypeError as exc:
        raise ValueError("arrival_rates deve ser um iteravel com numeros >= 0.") from exc

    if not rates:
        raise ValueError("arrival_rates nao pode ser vazio.")

    for idx, rate in enumerate(rates, start=1):
        if rate < 0:
            raise ValueError(f"lambda_{idx} deve ser >= 0.")
    return rates


def validate_common_inputs(rates: Iterable[float], mu: float, s: int) -> List[float]:
    clean_rates = coerce_arrival_rates(rates)

    if mu <= 0:
        raise ValueError("mu deve ser > 0.")
    if not isinstance(s, int) or s <= 0:
        raise ValueError("s deve ser inteiro >= 1.")

    total_lambda = sum(clean_rates)
    capacity = s * mu
    if total_lambda >= capacity and capacity > 0:
        raise ValueError(
            f"Sistema instavel: lambda_total={total_lambda:.6f} >= s*mu = {capacity:.6f}."
        )
    return clean_rates


def prefix_sums(values: List[float]) -> List[float]:
    result: List[float] = []
    running = 0.0
    for value in values:
        running += value
        result.append(running)
    return result


def erlang_c(lmbda: float, mu: float, s: int) -> float:
    if lmbda <= 0:
        return 0.0

    rho = lmbda / (s * mu)
    if rho >= 1:
        raise ValueError(
            f"Subfila com lambda={lmbda:.6f} e s*mu={s*mu:.6f} e instavel (rho={rho:.6f} >= 1)."
        )

    a = lmbda / mu
    sum_terms = sum((a**k) / factorial(k) for k in range(s))
    last_term = (a**s) / (factorial(s) * (1 - rho))
    p0 = 1.0 / (sum_terms + last_term)
    return last_term * p0


def aggregate_totals(class_metrics: List[Dict[str, float]], mu: float, s: int) -> Dict[str, Any]:
    total_lambda = sum(cls["lambda"] for cls in class_metrics)
    total_L = sum(cls["L"] for cls in class_metrics)
    total_Lq = sum(cls["Lq"] for cls in class_metrics)
    service_time = (total_lambda / mu) if mu > 0 else 0.0
    if total_lambda > 0:
        W = total_L / total_lambda
        Wq = total_Lq / total_lambda
    else:
        W = Wq = 0.0

    rho = total_lambda / (s * mu) if mu > 0 else 0.0

    if s == 1:
        p0 = 1.0 - rho
    else:
        a = total_lambda / mu
        sum_terms = sum((a**k) / factorial(k) for k in range(s))
        last_term = (a**s) / (factorial(s) * (1 - rho))
        p0 = 1.0 / (sum_terms + last_term)

    return {
        "rho": rho,
        "p0": p0,
        "L": total_L,
        "Lq": total_Lq,
        "W": W,
        "Wq": Wq,
        "per_class": class_metrics,
        "lambda_total": total_lambda,
        "service_in_progress": service_time,
    }