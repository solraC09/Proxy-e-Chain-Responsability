
from abc import ABC, abstractmethod


class IUsuario(ABC):
    @abstractmethod
    def get_nome(self) -> str: ...

    @abstractmethod
    def get_cpf(self) -> str: ...

    @abstractmethod
    def get_endereco(self) -> str: ...


class Usuario(IUsuario):
    def __init__(self, nome: str, cpf: str, endereco: str):
        self._nome = nome
        self._cpf = cpf
        self._endereco = endereco

    def get_nome(self) -> str:
        return self._nome

    def get_cpf(self) -> str:
        return self._cpf

    def get_endereco(self) -> str:
        return self._endereco


class UsuarioProxy(IUsuario):
    def __init__(self, usuario: Usuario):
        self._usuario = usuario
        
    def get_nome(self) -> str:
        return self._usuario.get_nome()

    def get_cpf(self) -> str:
        digitos = "".join(c for c in self._usuario.get_cpf() if c.isdigit())
        if len(digitos) != 11:
            raise ValueError("CPF inválido: deve conter 11 dígitos.")
        meio = digitos[3:9]  
        return f"***.{meio[:3]}.{meio[3:]}-**"

    def get_endereco(self) -> str:
        raise PermissionError(
        )


class Principal:
    @staticmethod
    def exibir_dados(usuario: IUsuario) -> None:
        print(f"Nome    : {usuario.get_nome()}")
        print(f"CPF     : {usuario.get_cpf()}")
        try:
            print(f"Endereço: {usuario.get_endereco()}")
        except PermissionError as erro:
            print(f"Endereço: [BLOQUEADO] {erro}")

    @staticmethod
    def main() -> None:
        real = Usuario("Maria Silva", "123.456.789-09", "Rua das Flores, 100 - Rio de Janeiro")

        print("=== Acesso direto ao Usuario (sem proxy) ===")
        Principal.exibir_dados(real)

        print("\n=== Acesso via UsuarioProxy (com LGPD) ===")
        Principal.exibir_dados(UsuarioProxy(real))


if __name__ == "__main__":
    Principal.main()
