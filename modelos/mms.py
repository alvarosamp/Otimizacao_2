from math import exp, factorial
from typing import Any, Dict


def mms(
    lmbda: float,
    mu: float,
    s: int,
    n: int | None = None,
    t: float | None = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Modelo M/M/s com capacidade infinita.

    Parametros opcionais:
      - n: calcula Pn
      - t: calcula P(W>t) e P(Wq>t) usando Erlang C
    """
    if lmbda < 0:
        raise ValueError("lambda (lmbda) deve ser >= 0")
    if mu <= 0:
        raise ValueError("mu deve ser > 0")
    if not isinstance(s, int) or s <= 0:
        raise ValueError("s deve ser inteiro >= 1")

    if lmbda == 0:
        result: Dict[str, Any] = {
            "rho": 0.0,
            "p0": 1.0,
            "L": 0.0,
            "Lq": 0.0,
            "W": 0.0,
            "Wq": 0.0,
        }
        if n is not None:
            result["pn"] = 1.0 if n == 0 else 0.0
        if t is not None:
            result["P(W>t)"] = 0.0
            result["P(Wq>t)"] = 0.0
        return result

    rho = lmbda / (s * mu)
    if rho >= 1:
        raise ValueError(f"Sistema instavel (rho = {rho:.6f} >= 1).")

    a = lmbda / mu
    sum1 = sum(a**k / factorial(k) for k in range(s))
    sum2 = (a**s) / (factorial(s) * (1 - rho))
    p0 = 1.0 / (sum1 + sum2)

    def pn_func(n_val: int) -> float:
        if n_val < 0 or int(n_val) != n_val:
            raise ValueError("n deve ser inteiro >= 0")
        if n_val <= s:
            return (a**n_val / factorial(n_val)) * p0
        return (a**n_val / (factorial(s) * (s ** (n_val - s)))) * p0

    Lq = p0 * (a**s) * rho / (factorial(s) * (1 - rho) ** 2)
    L = Lq + a
    Wq = Lq / lmbda
    W = L / lmbda

    result: Dict[str, Any] = {
        "rho": rho,
        "p0": p0,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
    }

    if n is not None:
        result["pn"] = pn_func(n)

    if t is not None:
        if t < 0:
            raise ValueError("t deve ser >= 0")

        C = (a**s / (factorial(s) * (1 - rho))) * p0
        PWq_gt_t = C * exp(-(1 - rho) * s * mu * t)

        denom = (s - 1) - a
        if abs(denom) < 1e-8:
            inner = C * (mu * t)
        else:
            inner = C * (1 - exp(-mu * t * denom)) / denom

        PW_gt_t = exp(-mu * t) * (1 + inner)

        result["P(Wq>t)"] = PWq_gt_t
        result["P(W>t)"] = PW_gt_t

    return result