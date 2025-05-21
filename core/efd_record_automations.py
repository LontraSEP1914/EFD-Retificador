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

def aplicar_logica_utilizacao_credito_m100(registro_m100, todos_os_registros=None) -> bool:
    """
    Aplica a lógica de utilização de crédito para o registro M100.
    Baseado na entrada do VL_CRED_UTIL_PER (campo índice 15), calcula:
    - IND_UTIL_CRED_PER (campo índice 14)
    - VL_CRED_DIF (campo índice 16)
    Utiliza VL_CRED (campo índice 7) como o crédito total disponível.
    """
    try:
        idx_vl_cred_apurado = 11
        idx_ind_util = 12
        idx_vl_cred_util_per = 13 # Campo que o usuário edita, gatilho da regra
        idx_vl_cred_dif = 14

        vl_cred_apurado_str = registro_m100.obter_campo(idx_vl_cred_apurado)
        vl_cred_util_per_str = registro_m100.obter_campo(idx_vl_cred_util_per)

        if vl_cred_apurado_str is None or vl_cred_util_per_str is None:
            print("M100: Campo VL_CRED ou VL_CRED_UTIL_PER não encontrado.")
            return False

        # Converter para Decimal para cálculos precisos
        cred_apurado = Decimal(vl_cred_apurado_str.replace(',', '.'))
        cred_utilizado = Decimal(vl_cred_util_per_str.replace(',', '.'))

        novo_ind_util = ""
        modificado_ind = False
        modificado_dif = False

        # Lógica para IND_UTIL_CRED_PER (campo idx_ind_util)
        # "caso seja usado o valor total do campo 12 (VL_CRED), o campo 13 (IND_UTIL) fica com zero, 
        # caso contrário, ele vira 1"
        if cred_utilizado < Decimal('0'):
            print("M100: Valor do Crédito Utilizado não pode ser negativo.")
            # Poderíamos aqui lançar um erro ou notificar o usuário na GUI de forma mais explícita.
            # Por ora, não faremos alterações.
            return False 
        
        if cred_utilizado > cred_apurado:
            print(f"M100: Alerta! Crédito utilizado ({cred_utilizado}) maior que o disponível ({cred_apurado}). Ajustando utilizado para o máximo disponível.")
            # Ajusta o crédito utilizado para não exceder o apurado.
            # Ou poderíamos retornar False e exigir correção manual.
            # Para este exemplo, vamos ajustar e continuar.
            cred_utilizado = cred_apurado 
            novo_vl_cred_util_per_str = f"{cred_utilizado:.2f}".replace('.', ',')
            if registro_m100.obter_campo(idx_vl_cred_util_per) != novo_vl_cred_util_per_str:
                 registro_m100.definir_campo(idx_vl_cred_util_per, novo_vl_cred_util_per_str)
                 # Como este campo é o "gatilho", a reexibição dos detalhes na GUI o mostrará atualizado.

        if cred_apurado > Decimal('0'): # Só faz sentido definir 0 ou 1 se havia crédito.
            if cred_utilizado == cred_apurado:
                novo_ind_util = "0" # Uso total
            else: # Inclui cred_utilizado < cred_apurado (e cred_utilizado >= 0)
                novo_ind_util = "1" # Uso parcial
        else: # Se não há crédito apurado, o indicador pode não se aplicar ou ser "1"
            novo_ind_util = "1" # Ou "" (vazio), dependendo da especificação para VL_CRED = 0

        valor_antigo_ind = registro_m100.obter_campo(idx_ind_util)
        if valor_antigo_ind != novo_ind_util:
            registro_m100.definir_campo(idx_ind_util, novo_ind_util)
            modificado_ind = True

        # Lógica para VL_CRED_DIF (campo idx_vl_cred_dif)
        # "o campo 15 (VL_CRED_DIF) é a subtração dos campos 12 (VL_CRED) e 14 (VL_CRED_UTIL_PER)"
        cred_diferir = cred_apurado - cred_utilizado
        novo_vl_cred_dif_str = f"{cred_diferir:.2f}".replace('.', ',')

        valor_antigo_dif = registro_m100.obter_campo(idx_vl_cred_dif)
        if valor_antigo_dif != novo_vl_cred_dif_str:
            registro_m100.definir_campo(idx_vl_cred_dif, novo_vl_cred_dif_str)
            modificado_dif = True
        
        if modificado_ind or modificado_dif:
            print(f"Regra 'aplicar_logica_utilizacao_credito_m100' aplicada. IND_UTIL: {novo_ind_util}, VL_CRED_DIF: {novo_vl_cred_dif_str}")
            return True
        else:
            print("Regra 'aplicar_logica_utilizacao_credito_m100': Nenhuma alteração efetiva nos campos calculados.")
            return False

    except InvalidOperation:
        print(f"M100: Erro de conversão de valor numérico. Verifique os campos de valores.")
        return False
    except Exception as e:
        print(f"Erro ao aplicar regra 'aplicar_logica_utilizacao_credito_m100': {e}")
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
if "M100" not in regras_disponiveis:
    regras_disponiveis["M100"] = []

regras_disponiveis["M100"].append(
    {
        "nome_exibicao": "Aplicar Lógica de Uso de Crédito (M100)",
        "funcao": aplicar_logica_utilizacao_credito_m100,
        "descricao": "Calcula o Indicador de Uso e o Saldo a Diferir com base no Crédito Disponível e no Crédito Utilizado no período."
    }
)