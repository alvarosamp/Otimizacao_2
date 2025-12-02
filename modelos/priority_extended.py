from typing import Any, Dict, Iterable, List

from .priority_common import coerce_arrival_rates
from .mms_priority_non_preemptive import mms_priority_non_preemptive
from .mms_priority_preemptive import mms_priority_preemptive


MIN_PRIORITY_CLASSES = 1
MAX_SERVERS = 3


def _enforce_minimums(arrival_rates: Iterable[float], s: int) -> List[float]:
    """
    Garante que o modelo seja usado com pelo menos 1 classe de prioridade e no maximo 3 servidores.
    Retorna as taxas convertidas para float para reaproveitar nas funcoes base.
    """
    rates = coerce_arrival_rates(arrival_rates)
    if len(rates) < MIN_PRIORITY_CLASSES:
        raise ValueError(f"Informe pelo menos {MIN_PRIORITY_CLASSES} classe de prioridade.")
    if not isinstance(s, int) or s < 1:
        raise ValueError("Numero de servidores (s) deve ser um inteiro >= 1.")
    if s > MAX_SERVERS:
        raise ValueError(f"Numero de servidores (s) deve ser <= {MAX_SERVERS}.")
    return rates


def priority_with_preemption(
    arrival_rates: Iterable[float],
    mu: float,
    s: int = MAX_SERVERS,
) -> Dict[str, Any]:
    """
    Modelo M/M/s com prioridades preemptivas para pelo menos 3 classes e ate 3 servidores.
    A logica de calculo reaproveita o modelo geral de prioridade preemptiva (mms).
    """
    rates = _enforce_minimums(arrival_rates, s)
    return mms_priority_preemptive(rates, mu, s)


def priority_without_preemption(
    arrival_rates: Iterable[float],
    mu: float,
    s: int = MAX_SERVERS,
) -> Dict[str, Any]:
    """
    Modelo M/M/s com prioridades nao preemptivas para pelo menos 3 classes e ate 3 servidores.
    Utiliza o calculo geral de prioridade nao preemptiva (mms).
    """
    rates = _enforce_minimums(arrival_rates, s)
    return mms_priority_non_preemptive(rates, mu, s)