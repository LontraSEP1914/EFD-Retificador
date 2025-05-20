# core/efd_parser.py

from .efd_structures import RegistroEFD  # Importa a classe que definimos

def parse_efd_file(filepath: str) -> list[RegistroEFD]:
    """
    Lê um arquivo EFD Contribuições (.txt) e faz o parse das linhas em objetos RegistroEFD.

    Args:
        filepath (str): O caminho para o arquivo .txt da EFD Contribuições.

    Returns:
        list[RegistroEFD]: Uma lista de objetos RegistroEFD representando o arquivo.
                           Retorna uma lista vazia em caso de erro ao abrir o arquivo
                           ou se o arquivo estiver vazio.
    """
    registros: list[RegistroEFD] = []
    try:
        # EFD Contribuições usualmente utiliza a codificação 'latin-1' ou 'cp1252'
        with open(filepath, 'r', encoding='latin-1') as file:
            for linha_num, linha_str in enumerate(file, 1):
                linha_str = linha_str.strip()

                if not linha_str:  # Pula linhas em branco
                    continue

                # Verifica se a linha tem o formato mínimo esperado (começa e termina com pipe)
                if not linha_str.startswith('|') or not linha_str.endswith('|'):
                    print(f"Alerta: Linha {linha_num} não parece ser um registro EFD válido (não começa/termina com '|'): '{linha_str[:50]}...'")
                    continue

                # Remove o pipe inicial e final para facilitar o split
                # Ex: "|0000|LEIAUTE|..." -> "0000|LEIAUTE|..."
                campos_str = linha_str[1:-1]
                
                # Divide a string pelos campos usando o delimitador '|'
                lista_de_campos = campos_str.split('|')

                if not lista_de_campos or not lista_de_campos[0]: # Deve haver pelo menos o tipo do registro
                    print(f"Alerta: Linha {linha_num} resultou em campos vazios ou tipo de registro ausente: '{linha_str[:50]}...'")
                    continue
                
                tipo_registro = lista_de_campos[0]
                
                # Cria o objeto RegistroEFD
                registro = RegistroEFD(tipo_registro=tipo_registro, campos=lista_de_campos)
                registros.append(registro)

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{filepath}'")
        return []
    except Exception as e:
        print(f"Erro ao processar o arquivo '{filepath}': {e}")
        return []
        
    return registros

# Exemplo de uso (para teste, pode ser movido para um script de teste ou main.py depois):
# if __name__ == '__main__':
#     # Crie um arquivo dummy_efd.txt para testar, por exemplo:
#     # |0000|LAYOUT_TESTE|0|NOME DA EMPRESA TESTE|12345678000199|SP|12345|NIRE|0|1|
#     # |0001|0|
#     # |M001|0|
#     # |M200|150.75|0.00|150.75|01012025|1|DOCUMENTO XPTO|
#     # |M210|C101|1.65|100.00|1.65|COD_AJUSTE_EXEMPLO|
#     # |1001|0|
#     # |1990|3|
#
#     # Crie um arquivo chamado dummy_efd.txt no mesmo diretório do efd_parser.py
#     # com o conteúdo de exemplo acima para testar.
    # dummy_file_path = 'efd_retificador/core/dummy_efd.txt' 
    # parsed_registros = parse_efd_file(dummy_file_path)

    # if parsed_registros:
    #     print(f"Total de registros lidos: {len(parsed_registros)}")
    #     for reg in parsed_registros:
    #         print(f"  {reg} -> Linha Original: {reg.para_linha_txt()}")
    #         if reg.tipo_registro == "M200":
    #             print(f"    Campo 1 (Valor Total Contribuição): {reg.obter_campo(1)}") # VL_TOT_CONT_NC_PER
    #             print(f"    Campo 6 (Documento): {reg.obter_campo(6)}") # NUM_DOC
    # else:
    #     print("Nenhum registro foi lido ou houve um erro.")