from typing import Any, Dict


def mg1(
    lmbda: float,
    mu: float,
    service_distribution: str = "poisson",
    **kwargs,
) -> Dict[str, Any]:
    """
    Modelo M/G/1 (capacidade infinita, disciplina FCFS).

    `service_distribution` define como os momentos do servico sao estimados:
      - "poisson": Var(S) = E[S]
      - "exponential": Var(S) = (E[S])^2
      - "deterministic": Var(S) = 0
    """
    if lmbda < 0:
        raise ValueError("lambda (lmbda) deve ser >= 0")
    if mu <= 0:
        raise ValueError("mu deve ser > 0")

    mean_service = 1.0 / mu
    dist = (service_distribution or "poisson").strip().lower()

    if dist == "poisson":
        variance = mean_service
    elif dist == "exponential":
        variance = mean_service**2
    elif dist == "deterministic":
        variance = 0.0
    else:
        raise ValueError(
            "service_distribution deve ser 'poisson', 'exponential' ou 'deterministic'."
        )

    ES2 = variance + mean_service**2
    cs2 = variance / (mean_service**2) if mean_service > 0 else 0.0

    rho = lmbda * mean_service
    if rho >= 1:
        raise ValueError(f"Sistema instavel (rho = {rho:.6f} >= 1).")

    if lmbda == 0:
        return {
            "rho": 0.0,
            "p0": 1.0,
            "L": 0.0,
            "Lq": 0.0,
            "W": mean_service,
            "Wq": 0.0,
            "E[S]": mean_service,
            "E[S^2]": ES2,
            "Var(S)": variance,
            "cs2": cs2,
        }

    Wq = (lmbda * ES2) / (2.0 * (1.0 - rho))
    W = Wq + mean_service
    Lq = lmbda * Wq
    L = Lq + rho
    p0 = 1.0 - rho

    return {
        "rho": rho,
        "p0": p0,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "E[S]": mean_service,
        "E[S^2]": ES2,
        "Var(S)": variance,
        "cs2": cs2,
    }