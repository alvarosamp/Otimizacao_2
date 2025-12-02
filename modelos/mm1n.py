from typing import Any, Dict


def _comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1

    num = 1
    den = 1
    for i in range(1, k + 1):
        num *= n - (k - i)
        den *= i
    return num // den


def mm1n(
    lmbda: float,
    mu: float,
    N: int,
    n: int | None = None,
    t: float | None = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Modelo M/M/1/N (populacao finita).
    """
    if lmbda < 0:
        raise ValueError("lambda (lmbda) deve ser >= 0")
    if mu <= 0:
        raise ValueError("mu deve ser > 0")
    if not isinstance(N, int) or N < 0:
        raise ValueError("N deve ser inteiro >= 0")

    if N == 0:
        result: Dict[str, Any] = {
            "rho": 0.0,
            "p0": 1.0,
            "L": 0.0,
            "Lq": 0.0,
            "W": 0.0,
            "Wq": 0.0,
            "lambda_eff": 0.0,
            "L_operational": 0.0,
        }
        if n is not None:
            result["pn"] = 1.0 if n == 0 else 0.0
        return result

    r = lmbda / mu
    denom = sum(_comb(N, k) * (r**k) for k in range(N + 1))
    p0 = 1.0 / denom

    pn_values = [_comb(N, k) * (r**k) * p0 for k in range(N + 1)]

    def pn_func(n_val: int) -> float:
        if n_val < 0 or int(n_val) != n_val or n_val > N:
            raise ValueError(f"n deve ser inteiro entre 0 e {N}")
        return pn_values[n_val]

    L = sum(k * pn_values[k] for k in range(N + 1))
    Lq = L - (1 - p0)
    lambda_eff = lmbda * (N - L)

    if lambda_eff > 0:
        W = L / lambda_eff
        Wq = Lq / lambda_eff
    else:
        W = Wq = 0.0

    L_operational = N - L

    result: Dict[str, Any] = {
        "rho": N * lmbda / mu,
        "p0": p0,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "lambda_eff": lambda_eff,
        "L_operational": L_operational,
    }

    if n is not None:
        result["pn"] = pn_func(n)

    return result