# core/efd_structures.py

class RegistroEFD:
    def __init__(self, tipo_registro: str, campos: list[str]):
        """
        Representa um registro (linha) de um arquivo EFD.

        Args:
            tipo_registro (str): O tipo do registro (ex: "0000", "M200", "C170").
                                 Este é o primeiro campo da lista de campos.
            campos (list[str]): Uma lista de strings, onde cada string é um campo do registro.
                                O primeiro elemento DEVE ser o tipo do registro.
        """
        if not campos or campos[0] != tipo_registro:
            # Adicionando uma verificação básica, embora o parser vá garantir isso.
            # Poderíamos levantar um erro ou ajustar, mas por ora é mais uma nota.
            # Idealmente, o tipo_registro é derivado dos campos no momento da criação.
            # Ou o parser garante que campos[0] é o tipo_registro.
            pass

        self.tipo_registro: str = tipo_registro
        self.campos: list[str] = campos # A lista completa, incluindo o tipo_registro como campos[0]

    def __repr__(self) -> str:
        return f"RegistroEFD(tipo='{self.tipo_registro}', num_campos={len(self.campos)})"

    def obter_campo(self, indice: int) -> str | None:
        """
        Retorna o valor de um campo pelo seu índice (base 0).
        Lembre-se que o campo 0 é o próprio tipo do registro.
        O campo "1" na especificação da EFD (ex: CNPJ no registro 0000) é o índice 1 na nossa lista.
        """
        if 0 <= indice < len(self.campos):
            return self.campos[indice]
        return None

    def definir_campo(self, indice: int, valor: str) -> bool:
        """
        Define o valor de um campo pelo seu índice.
        Não permite alterar o tipo do registro (campo 0) por este método.
        """
        if 0 < indice < len(self.campos): # Não permite alterar o campo 0 (tipo)
            self.campos[indice] = valor
            return True
        # Se quiser permitir criar novos campos (ex: se a linha original era menor)
        # elif indice >= len(self.campos) and indice > 0:
        #     # Preenche com campos vazios se necessário
        #     self.campos.extend([""] * (indice - len(self.campos) + 1))
        #     self.campos[indice] = valor
        #     return True
        return False

    def para_linha_txt(self) -> str:
        """
        Converte o registro de volta para o formato de linha do arquivo .txt.
        """
        return f"|{'|'.join(self.campos)}|"

# Exemplo de uso (apenas para teste, não ficaria aqui):
# if __name__ == '__main__':
#     # Suponha que 'campos_lidos' seja ['M200', '100.00', '01', 'Detalhes...']
#     campos_lidos_exemplo = ['M200', '100.00', '01', 'Detalhes do registro M200']
#     reg = RegistroEFD(tipo_registro=campos_lidos_exemplo[0], campos=campos_lidos_exemplo)
#     print(reg)
#     print(f"Campo 1 (Valor da Contribuição no M200 hipotético): {reg.obter_campo(1)}")
#     reg.definir_campo(1, "150.50")
#     print(f"Campo 1 Modificado: {reg.obter_campo(1)}")
#     print(f"Linha TXT: {reg.para_linha_txt()}")

#     campos_0000_exemplo = ["0000", "LEIAUTE_CONTRIB_007", "0", "NOME EMPRESA", "12345678000199", "UF", "1234567", "", "0", "1"]
#     reg_0000 = RegistroEFD(campos_0000_exemplo[0], campos_0000_exemplo)
#     print(reg_0000)
#     print(reg_0000.para_linha_txt())