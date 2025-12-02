from math import factorial
from typing import Any, Dict


def mmsk(
    lmbda: float,
    mu: float,
    s: int,
    K: int,
    n: int | None = None,
    t: float | None = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Modelo M/M/s/K com capacidade total K.

    Parametros opcionais:
      - n: calcula Pn
      - t: aceito, mas nao utilizado
    """
    if lmbda < 0:
        raise ValueError("lambda (lmbda) deve ser >= 0")
    if mu <= 0:
        raise ValueError("mu deve ser > 0")
    if not isinstance(s, int) or s <= 0:
        raise ValueError("s deve ser inteiro >= 1")
    if not isinstance(K, int) or K < 0:
        raise ValueError("K deve ser inteiro >= 0")
    if K < s:
        raise ValueError("K deve ser >= s")

    if lmbda == 0:
        result: Dict[str, Any] = {
            "rho": 0.0,
            "p0": 1.0,
            "L": 0.0,
            "Lq": 0.0,
            "W": 0.0,
            "Wq": 0.0,
            "lambda_eff": 0.0,
        }
        if n is not None:
            result["pn"] = 1.0 if n == 0 else 0.0
        return result

    rho = lmbda / (s * mu)
    a = lmbda / mu

    sum1 = sum(a**n_state / factorial(n_state) for n_state in range(s + 1))
    sum2 = sum(
        (a**n_state) / (factorial(s) * (s ** (n_state - s)))
        for n_state in range(s + 1, K + 1)
    )
    p0 = 1.0 / (sum1 + sum2)

    def pn_func(n_val: int) -> float:
        if n_val < 0 or int(n_val) != n_val or n_val > K:
            raise ValueError(f"n deve ser inteiro entre 0 e {K}")
        if n_val <= s:
            return (a**n_val / factorial(n_val)) * p0
        return (a**n_val / (factorial(s) * (s ** (n_val - s)))) * p0

    if abs(1 - rho) < 1e-10:
        raise ValueError("Caso rho  1 nao suportado para Lq em M/M/s/K.")

    factor = p0 * (a**s) * rho / (factorial(s) * (1 - rho) ** 2)
    tail = 1 - rho ** (K - s) - (K - s) * (1 - rho) * rho ** (K - s)
    Lq = factor * tail

    sum_pn = [pn_func(nv) for nv in range(s)]
    L_partial = sum(nv * pn_func(nv) for nv in range(s))
    prob_busy = 1 - sum(sum_pn)
    L = L_partial + Lq + s * prob_busy

    pK = pn_func(K)
    lambda_eff = lmbda * (1 - pK)

    if lambda_eff > 0:
        W = L / lambda_eff
        Wq = Lq / lambda_eff
    else:
        W = Wq = 0.0

    result: Dict[str, Any] = {
        "rho": rho,
        "p0": p0,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "lambda_eff": lambda_eff,
        "pK": pK,
    }

    if n is not None:
        result["pn"] = pn_func(n)

    return result