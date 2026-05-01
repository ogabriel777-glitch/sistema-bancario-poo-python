"""
Sistema Bancário - Modelagem com POO em Python
==============================================
Autor: Gabriel Alves
Desafio: Modelando o Sistema Bancário em POO com Python - DIO
Descrição: Sistema bancário completo utilizando Programação Orientada a Objetos,
           com suporte a múltiplos clientes, contas e histórico de transações.
"""

import textwrap
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


# ==================== TRANSAÇÕES ====================

class Transacao(ABC):
    """Classe abstrata base para todas as transações bancárias."""

    @property
    @abstractmethod
    def valor(self) -> float:
        pass

    @abstractmethod
    def registrar(self, conta: "Conta") -> None:
        pass


class Deposito(Transacao):
    """Representa uma transação de depósito."""

    def __init__(self, valor: float) -> None:
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: "Conta") -> None:
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


class Saque(Transacao):
    """Representa uma transação de saque."""

    def __init__(self, valor: float) -> None:
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: "Conta") -> None:
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


# ==================== HISTÓRICO ====================

class Historico:
    """Armazena o histórico de transações de uma conta."""

    def __init__(self) -> None:
        self._transacoes: list[dict] = []

    @property
    def transacoes(self) -> list[dict]:
        return self._transacoes

    def adicionar_transacao(self, transacao: Transacao) -> None:
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })

    def gerar_relatorio(self) -> str:
        """Gera um relatório formatado de todas as transações."""
        if not self._transacoes:
            return "Nenhuma movimentação realizada."

        relatorio = ""
        for t in self._transacoes:
            tipo = "⬆ Depósito" if t["tipo"] == "Deposito" else "⬇ Saque"
            relatorio += f"\n{tipo}:\t R$ {t['valor']:.2f}  [{t['data']}]"
        return relatorio


# ==================== CONTAS ====================

class Conta:
    """Classe base para contas bancárias."""

    def __init__(self, numero: int, cliente: "Cliente") -> None:
        self._saldo: float = 0.0
        self._numero: int = numero
        self._agencia: str = "0001"
        self._cliente: "Cliente" = cliente
        self._historico: Historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: "Cliente", numero: int) -> "Conta":
        return cls(numero, cliente)

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def agencia(self) -> str:
        return self._agencia

    @property
    def cliente(self) -> "Cliente":
        return self._cliente

    @property
    def historico(self) -> Historico:
        return self._historico

    def sacar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ Operação falhou! Saldo insuficiente. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True


class ContaCorrente(Conta):
    """Conta corrente com limite de saque e número máximo de saques diários."""

    LIMITE_PADRAO: float = 500.0
    LIMITE_SAQUES_PADRAO: int = 3

    def __init__(
        self,
        numero: int,
        cliente: "Cliente",
        limite: float = LIMITE_PADRAO,
        limite_saques: int = LIMITE_SAQUES_PADRAO,
    ) -> None:
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    @property
    def limite(self) -> float:
        return self._limite

    @property
    def limite_saques(self) -> int:
        return self._limite_saques

    def sacar(self, valor: float) -> bool:
        saques_realizados = sum(
            1 for t in self.historico.transacoes if t["tipo"] == Saque.__name__
        )

        if valor > self._limite:
            print(f"\n@@@ Operação falhou! O valor excede o limite de R$ {self._limite:.2f}. @@@")
            return False

        if saques_realizados >= self._limite_saques:
            print(f"\n@@@ Operação falhou! Limite de {self._limite_saques} saques diários atingido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self) -> str:
        return (
            f"Agência:\t{self.agencia}\n"
            f"C/C:\t\t{self.numero}\n"
            f"Titular:\t{self.cliente.nome}\n"
            f"Saldo:\t\tR$ {self.saldo:.2f}"
        )


# ==================== CLIENTES ====================

class Cliente:
    """Classe base para clientes do banco."""

    def __init__(self, endereco: str) -> None:
        self.endereco = endereco
        self.contas: list[Conta] = []

    def realizar_transacao(self, conta: Conta, transacao: Transacao) -> None:
        transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta) -> None:
        self.contas.append(conta)


class PessoaFisica(Cliente):
    """Cliente do tipo Pessoa Física, identificado por CPF."""

    def __init__(self, nome: str, data_nascimento: str, cpf: str, endereco: str) -> None:
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    def __str__(self) -> str:
        return f"{self.nome} (CPF: {self.cpf})"


# ==================== FUNÇÕES DO SISTEMA ====================

def menu() -> str:
    opcoes = """\n
    ╔══════════════════════════════╗
    ║        BANCO DIO - MENU      ║
    ╠══════════════════════════════╣
    ║  [d]  Depositar              ║
    ║  [s]  Sacar                  ║
    ║  [e]  Extrato                ║
    ║  [nc] Nova Conta             ║
    ║  [lc] Listar Contas          ║
    ║  [nu] Novo Usuário           ║
    ║  [q]  Sair                   ║
    ╚══════════════════════════════╝
    => """
    return input(textwrap.dedent(opcoes)).strip().lower()


def filtrar_cliente(cpf: str, clientes: list[Cliente]) -> Optional[Cliente]:
    resultado = [c for c in clientes if isinstance(c, PessoaFisica) and c.cpf == cpf]
    return resultado[0] if resultado else None


def selecionar_conta(cliente: Cliente) -> Optional[Conta]:
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta cadastrada! @@@")
        return None

    if len(cliente.contas) == 1:
        return cliente.contas[0]

    print("\n=== Contas disponíveis ===")
    for i, conta in enumerate(cliente.contas, 1):
        print(f"[{i}] Conta {conta.numero} | Ag. {conta.agencia}")

    try:
        escolha = int(input("Selecione o número da conta: ")) - 1
        if 0 <= escolha < len(cliente.contas):
            return cliente.contas[escolha]
        print("\n@@@ Opção inválida! @@@")
    except ValueError:
        print("\n@@@ Entrada inválida! @@@")

    return None


def obter_cliente(clientes: list[Cliente]) -> Optional[Cliente]:
    cpf = input("Informe o CPF do cliente (somente números): ").strip()
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
    return cliente


def depositar(clientes: list[Cliente]) -> None:
    cliente = obter_cliente(clientes)
    if not cliente:
        return

    conta = selecionar_conta(cliente)
    if not conta:
        return

    try:
        valor = float(input("Informe o valor do depósito: R$ "))
    except ValueError:
        print("\n@@@ Valor inválido! @@@")
        return

    cliente.realizar_transacao(conta, Deposito(valor))


def sacar(clientes: list[Cliente]) -> None:
    cliente = obter_cliente(clientes)
    if not cliente:
        return

    conta = selecionar_conta(cliente)
    if not conta:
        return

    try:
        valor = float(input("Informe o valor do saque: R$ "))
    except ValueError:
        print("\n@@@ Valor inválido! @@@")
        return

    cliente.realizar_transacao(conta, Saque(valor))


def exibir_extrato(clientes: list[Cliente]) -> None:
    cliente = obter_cliente(clientes)
    if not cliente:
        return

    conta = selecionar_conta(cliente)
    if not conta:
        return

    print("\n╔═══════════════ EXTRATO ════════════════╗")
    print(conta.historico.gerar_relatorio())
    print(f"\n  Saldo atual:\t R$ {conta.saldo:.2f}")
    print("╚════════════════════════════════════════╝")


def criar_cliente(clientes: list[Cliente]) -> None:
    cpf = input("Informe o CPF (somente números): ").strip()

    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Nome completo: ").strip()
    data_nascimento = input("Data de nascimento (dd/mm/aaaa): ").strip()
    endereco = input("Endereço (logradouro, nº - bairro - cidade/UF): ").strip()

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)

    print(f"\n=== Cliente '{nome}' criado com sucesso! ===")


def criar_conta(numero_conta: int, clientes: list[Cliente], contas: list[Conta]) -> None:
    cliente = obter_cliente(clientes)
    if not cliente:
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print(f"\n=== Conta {numero_conta} criada com sucesso para {cliente.nome}! ===")


def listar_contas(contas: list[Conta]) -> None:
    if not contas:
        print("\n@@@ Nenhuma conta cadastrada! @@@")
        return

    print(f"\n{'='*50}")
    for conta in contas:
        print(textwrap.dedent(str(conta)))
        print(f"{'='*50}")


# ==================== EXECUÇÃO PRINCIPAL ====================

def main() -> None:
    clientes: list[Cliente] = []
    contas: list[Conta] = []

    acoes = {
        "d":  lambda: depositar(clientes),
        "s":  lambda: sacar(clientes),
        "e":  lambda: exibir_extrato(clientes),
        "nu": lambda: criar_cliente(clientes),
        "nc": lambda: criar_conta(len(contas) + 1, clientes, contas),
        "lc": lambda: listar_contas(contas),
    }

    while True:
        opcao = menu()

        if opcao == "q":
            print("\nObrigado por usar o Banco DIO! Até logo. 👋")
            break

        acao = acoes.get(opcao)
        if acao:
            acao()
        else:
            print("\n@@@ Opção inválida! Por favor, escolha uma opção do menu. @@@")


if __name__ == "__main__":
    main()
