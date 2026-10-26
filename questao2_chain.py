
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


class TipoConta(Enum):
    COMUM = "Comum"
    PREMIUM = "Premium"


@dataclass
class Conta:
    titular: str
    saldo: Decimal
    tipo: TipoConta
    bloqueio_judicial: bool = False


@dataclass
class Transacao:
    conta: Conta
    valor: Decimal


@dataclass
class Resultado:
    autorizada: bool
    motivo: str


class RegraAutorizacao(ABC):
    def __init__(self) -> None:
        self._proximo: Optional[RegraAutorizacao] = None

    def set_proximo(self, proximo: RegraAutorizacao) -> RegraAutorizacao:
        self._proximo = proximo
        return proximo 

    def autorizar(self, transacao: Transacao) -> Resultado:
        erro = self._validar(transacao)
        if erro is not None:
            return Resultado(False, erro)  
        if self._proximo is not None:
            return self._proximo.autorizar(transacao)  
        return Resultado(True, "Todas as regras foram aprovadas.")

    @abstractmethod
    def _validar(self, transacao: Transacao) -> Optional[str]:
        """Retorna None se válida, ou a mensagem de erro se reprovada."""


class RegraSaldo(RegraAutorizacao):
    def _validar(self, t: Transacao) -> Optional[str]:
        if t.conta.saldo < t.valor:
            return f"Saldo insuficiente (saldo R$ {t.conta.saldo:.2f}, valor R$ {t.valor:.2f})."
        return None


class RegraValorMaximo(RegraAutorizacao):
    LIMITES = {
        TipoConta.COMUM: Decimal("1000.00"),
        TipoConta.PREMIUM: Decimal("10000.00"),
    }

    def _validar(self, t: Transacao) -> Optional[str]:
        limite = self.LIMITES[t.conta.tipo]
        if t.valor > limite:
            return f"Valor acima do limite da conta {t.conta.tipo.value} (R$ {limite:.2f})."
        return None


class RegraBloqueioJudicial(RegraAutorizacao):
    def _validar(self, t: Transacao) -> Optional[str]:
        if t.conta.bloqueio_judicial:
            return "Conta com bloqueio judicial."
        return None


class Principal:
    @staticmethod
    def montar_corrente() -> RegraAutorizacao:
        saldo = RegraSaldo()
        saldo.set_proximo(RegraValorMaximo()).set_proximo(RegraBloqueioJudicial())
        return saldo 

    @staticmethod
    def main() -> None:
        corrente = Principal.montar_corrente()

        cenarios = [
            ("Aprovada (conta Comum)", Conta("Ana", Decimal("500"), TipoConta.COMUM), Decimal("200")),
            ("Saldo insuficiente", Conta("Bruno", Decimal("100"), TipoConta.COMUM), Decimal("300")),
            ("Acima do limite Comum", Conta("Carla", Decimal("5000"), TipoConta.COMUM), Decimal("1500")),
            ("Premium dentro do limite", Conta("Diego", Decimal("20000"), TipoConta.PREMIUM), Decimal("9000")),
            ("Acima do limite Premium", Conta("Elisa", Decimal("20000"), TipoConta.PREMIUM), Decimal("12000")),
            ("Bloqueio judicial", Conta("Fábio", Decimal("5000"), TipoConta.COMUM, True), Decimal("100")),
        ]

        for nome, conta, valor in cenarios:
            r = corrente.autorizar(Transacao(conta, valor))
            status = "AUTORIZADA" if r.autorizada else "NEGADA"
            print(f"[{nome}] {conta.titular} -> R$ {valor:.2f}: {status} - {r.motivo}")


if __name__ == "__main__":
    Principal.main()
