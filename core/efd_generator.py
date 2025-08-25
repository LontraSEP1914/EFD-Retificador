# efd_generator.py

from .efd_structures import RegistroEFD # Para type hinting

def generate_efd_file(filepath: str, registros: list[RegistroEFD]) -> bool:
    """
    Gera um arquivo EFD Contribuições (.txt) a partir de uma lista de objetos RegistroEFD.

    Args:
        filepath (str): O caminho completo onde o arquivo será salvo.
        registros (list[RegistroEFD]): A lista de objetos RegistroEFD a serem escritos.

    Returns:
        bool: True se o arquivo foi salvo com sucesso, False caso contrário.
    """
    try:
        # Usar a mesma codificação do parser para consistência.
        # É importante garantir que a quebra de linha seja a padrão do sistema
        # ou a especificada pela EFD (CRLF - \r\n), mas o Python no modo texto
        # geralmente lida bem com isso ('\n' é convertido para a quebra de linha nativa).
        # Para EFD, o padrão é CRLF, mas o PVA costuma ser tolerante.
        # Se for estritamente necessário CRLF: open(..., newline='\r\n')
        with open(filepath, 'w', encoding='latin-1', newline='') as file: # newline='' para evitar duplas quebras de linha no Windows
            for registro in registros:
                file.write(registro.para_linha_txt() + '\n') # Adiciona a quebra de linha no final
        return True
    except IOError as e:
        print(f"Erro de I/O ao salvar o arquivo '{filepath}': {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado ao salvar o arquivo '{filepath}': {e}")
        return False

# Exemplo de uso (apenas para ilustração, não faz parte da lógica principal):
# if __name__ == '__main__':
#     # Supondo que você tenha uma lista de objetos RegistroEFD
#     from .efd_structures import RegistroEFD
#     lista_exemplo_registros = [
#         RegistroEFD("0000", ["0000", "LAYOUT_TESTE", "0", "NOME EMPRESA", "CNPJ", "UF", "IE", "", "0", "1"]),
#         RegistroEFD("M001", ["M001", "1"]),
#         RegistroEFD("M200", ["M200", "100.50", "0.00", "100.50", "01012025", "1", "DOC123"]),
#     ]
#     sucesso = generate_efd_file("efd_gerado_teste.txt", lista_exemplo_registros)
#     if sucesso:
#         print("Arquivo de teste gerado com sucesso: efd_gerado_teste.txt")
#     else:
#         print("Falha ao gerar arquivo de teste.")