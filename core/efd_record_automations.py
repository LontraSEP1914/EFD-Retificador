# core/efd_record_automations.py

"""
Define regras de automação aplicáveis a registros específicos da EFD Contribuições.
"""
from decimal import Decimal, InvalidOperation # Usar Decimal para precisão financeira

# --- Funções de Regra ---
# Cada função de regra deve aceitar o objeto 'registro' como primeiro argumento.
# Pode, opcionalmente, aceitar 'todos_os_registros' se precisar de contexto mais amplo.
# Deve retornar True se a regra foi aplicada com sucesso e modificou o registro,
# False caso contrário ou se houve erro.

def calcular_contribuicao_m210(registro_m210, todos_os_registros=None) -> bool:
    """
    Calcula o VL_CONT_APUR (campo 5) do registro M210.
    VL_CONT_APUR = VL_BC_CONT (campo 3) * (ALIQ_PIS (campo 4) / 100)
    """
    try:
        # Índices dos campos para M210:
        # 3: VL_BC_CONT
        # 4: ALIQ_PIS
        # 5: VL_CONT_APUR
        
        vl_bc_cont_str = registro_m210.obter_campo(3)
        aliq_pis_str = registro_m210.obter_campo(4)

        if vl_bc_cont_str is None or aliq_pis_str is None:
            print("M210: Campos de BC ou Alíquota não encontrados para cálculo.")
            return False

        # Converter para Decimal, tratando vírgula como separador decimal
        vl_bc_cont = Decimal(vl_bc_cont_str.replace(',', '.'))
        aliq_pis = Decimal(aliq_pis_str.replace(',', '.'))
        
        vl_cont_apur = (vl_bc_cont * (aliq_pis / Decimal('100'))).quantize(Decimal('0.01'))
        
        # Formatar de volta para string com vírgula decimal e duas casas
        vl_cont_apur_str = f"{vl_cont_apur:.2f}".replace('.', ',')
        
        # Atualizar o campo no registro
        valor_antigo = registro_m210.obter_campo(5)
        if valor_antigo != vl_cont_apur_str:
            registro_m210.definir_campo(5, vl_cont_apur_str)
            print(f"Regra 'calcular_contribuicao_m210' aplicada. VL_CONT_APUR: {vl_cont_apur_str}")
            return True
        else:
            print(f"Regra 'calcular_contribuicao_m210': VL_CONT_APUR já está correto ({vl_cont_apur_str}). Nenhuma alteração feita.")
            return False # Não houve modificação efetiva

    except InvalidOperation: # Erro na conversão para Decimal
        print(f"M210: Erro de conversão de valor numérico para cálculo da contribuição. Verifique os campos VL_BC_CONT e ALIQ_PIS.")
        return False
    except Exception as e:
        print(f"Erro ao aplicar regra 'calcular_contribuicao_m210' no M210: {e}")
        return False

# --- Dicionário de Regras Disponíveis ---
# Mapeia tipo_registro para uma lista de dicionários de regras.
# Cada dicionário de regra contém:
#   "nome_exibicao": O nome que aparecerá na GUI.
#   "funcao": A referência à função Python que executa a regra.
#   "descricao": Uma breve descrição da regra (para tooltips, por exemplo).

regras_disponiveis = {
    "M210": [
        {
            "nome_exibicao": "Calcular Contribuição PIS (M210)",
            "funcao": calcular_contribuicao_m210,
            "descricao": "Calcula o Valor da Contribuição Apurada (VL_CONT_APUR) baseado na Base de Cálculo e Alíquota."
        },
        # Adicionar mais regras para M210 aqui, se houver
    ],
    "0000": [
        # Exemplo de regra placeholder para outro registro
        # {
        #     "nome_exibicao": "Preencher Nome Padrão (Exemplo 0000)",
        #     "funcao": lambda reg, all_regs=None: reg.definir_campo(7, "EMPRESA EXEMPLO LTDA") if reg.obter_campo(7) != "EMPRESA EXEMPLO LTDA" else False, # Exemplo com lambda
        #     "descricao": "Define o nome da empresa para um valor padrão (demonstração)."
        # }
    ]
    # Adicionar outros tipos de registro e suas respectivas regras aqui
}