from math import exp
from typing import Any, Dict


def mm1(
    lmbda: float,
    mu: float,
    n: int | None = None,
    t: float | None = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Modelo M/M/1 com capacidade infinita.

    Parametros opcionais:
      - n: calcula Pn
      - t: calcula P(W>t) e P(Wq>t)
    """
    if lmbda < 0:
        raise ValueError("lambda (lmbda) deve ser >= 0")
    if mu <= 0:
        raise ValueError("mu deve ser > 0")

    rho = lmbda / mu
    if rho >= 1:
        raise ValueError(f"Sistema instavel (rho = {rho:.6f} >= 1).")

    p0 = 1 - rho

    def pn(n_val: int) -> float:
        if n_val < 0 or int(n_val) != n_val:
            raise ValueError("n deve ser inteiro >= 0")
        return p0 * (rho**n_val)

    L = rho / (1 - rho)
    Lq = (rho**2) / (1 - rho)
    W = L / lmbda
    Wq = Lq / lmbda

    result: Dict[str, Any] = {
        "rho": rho,
        "p0": p0,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
    }

    if n is not None:
        result["pn"] = pn(n)

    if t is not None:
        if t < 0:
            raise ValueError("t deve ser >= 0")

        PW_gt_t = exp(-mu * (1 - rho) * t)
        PWq_gt_t = rho * PW_gt_t

        result["P(W>t)"] = PW_gt_t
        result["P(Wq>t)"] = PWq_gt_t

    return result