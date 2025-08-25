# efd_record_automations.py

"""
Define regras de automação aplicáveis a registros específicos da EFD Contribuições.
"""
from decimal import Decimal, InvalidOperation # Usar Decimal para precisão financeira

# --- Funções de Regra ---
# Cada função de regra deve aceitar o objeto 'registro' como primeiro argumento.
# Pode, opcionalmente, aceitar 'todos_os_registros' se precisar de contexto mais amplo.
# Deve retornar True se a regra foi aplicada com sucesso e modificou o registro,
# False caso contrário ou se houve erro.

def calcular_contribuicao_m210(registro_m210, todos_os_registros=None) -> list[int] | None: 
    """
    Calcula o VL_CONT_APUR (campo 5) do registro M210.
    Retorna lista de índices de campos modificados, lista vazia se nada mudou, ou None em caso de erro.
    """
    campos_modificados_indices = [] 
    try:
        idx_vl_bc_cont = 3
        idx_aliq_pis = 4
        idx_vl_cont_apur = 5
        
        vl_bc_cont_str = registro_m210.obter_campo(idx_vl_bc_cont)
        aliq_pis_str = registro_m210.obter_campo(idx_aliq_pis)

        if vl_bc_cont_str is None or aliq_pis_str is None:
            print(f"M210 (Calc Contrib): Campos {idx_vl_bc_cont} ou {idx_aliq_pis} não encontrados.")
            return None # Erro: campo não encontrado

        vl_bc_cont = Decimal(vl_bc_cont_str.replace(',', '.'))
        aliq_pis = Decimal(aliq_pis_str.replace(',', '.'))
        
        vl_cont_apur_calculado = (vl_bc_cont * (aliq_pis / Decimal('100'))).quantize(Decimal('0.01'))
        vl_cont_apur_calculado_str = f"{vl_cont_apur_calculado:.2f}".replace('.', ',')
        
        valor_antigo_cont_apur = registro_m210.obter_campo(idx_vl_cont_apur)
        
        if valor_antigo_cont_apur != vl_cont_apur_calculado_str:
            registro_m210.definir_campo(idx_vl_cont_apur, vl_cont_apur_calculado_str)
            campos_modificados_indices.append(idx_vl_cont_apur) # Adiciona o índice do campo modificado
            print(f"Regra 'calcular_contribuicao_m210' aplicada. VL_CONT_APUR (campo {idx_vl_cont_apur}): {vl_cont_apur_calculado_str}")
        else:
            print(f"Regra 'calcular_contribuicao_m210': VL_CONT_APUR já está correto ({vl_cont_apur_calculado_str}). Nenhuma alteração.")
            # Nenhuma modificação, campos_modificados_indices permanecerá vazia
            
        return campos_modificados_indices # Retorna a lista (pode estar vazia)

    except InvalidOperation:
        print(f"M210 (Calc Contrib): Erro de conversão de valor. Verifique campos {idx_vl_bc_cont} e {idx_aliq_pis}.")
        return None # Erro de conversão
    except Exception as e:
        print(f"Erro ao aplicar regra 'calcular_contribuicao_m210': {e}")
        return None # Outro err

def aplicar_logica_utilizacao_credito_m100(registro_m100, todos_os_registros=None) -> list[int] | None:
    """
    Aplica a lógica de utilização de crédito para o registro M100.
    Baseado na entrada do VL_CRED_DESC (índice 13), calcula:
    - IND_DESC_CRED (índice 12)
    - SLD_CRED (índice 14)
    Utiliza VL_CRED_DISP (índice 11) como o crédito total disponível.
    Retorna lista de índices de campos modificados, lista vazia se nada mudou, ou None em caso de erro.
    """
    campos_modificados_indices = []
    try:
        idx_vl_cred_disponivel = 11
        idx_ind_desc_cred = 12
        idx_vl_cred_desc = 13     
        idx_sld_cred_a_diferir = 14

        vl_cred_disponivel_str = registro_m100.obter_campo(idx_vl_cred_disponivel)
        vl_cred_desc_str = registro_m100.obter_campo(idx_vl_cred_desc)

        if vl_cred_disponivel_str is None or vl_cred_desc_str is None:
            print(f"M100 (Lógica Uso): Campo {idx_vl_cred_disponivel} (VL_CRED_DISP) ou {idx_vl_cred_desc} (VL_CRED_DESC) não encontrado.")
            return None

        cred_disponivel = Decimal(vl_cred_disponivel_str.replace(',', '.'))
        cred_utilizado = Decimal(vl_cred_desc_str.replace(',', '.'))
        
        novo_ind_desc_cred = ""
        
        # Lógica para ajuste e verificação do VL_CRED_DESC (idx_vl_cred_desc)
        if cred_utilizado < Decimal('0'):
            print("M100 (Lógica Uso): Valor do Crédito Utilizado (VL_CRED_DESC) não pode ser negativo. Regra não aplicada.")
            return None
        
        if cred_utilizado > cred_disponivel:
            print(f"M100 (Lógica Uso): Alerta! Crédito Utilizado ({cred_utilizado}) maior que o Disponível ({cred_disponivel}). Ajustando VL_CRED_DESC para o máximo disponível.")
            cred_utilizado = cred_disponivel 
            novo_vl_cred_desc_str = f"{cred_utilizado:.2f}".replace('.', ',')
            if registro_m100.obter_campo(idx_vl_cred_desc) != novo_vl_cred_desc_str:
                 registro_m100.definir_campo(idx_vl_cred_desc, novo_vl_cred_desc_str)
                 campos_modificados_indices.append(idx_vl_cred_desc)

        # Lógica para IND_DESC_CRED (idx_ind_desc_cred)
        if cred_disponivel >= Decimal('0'):
            if cred_utilizado == cred_disponivel:
                novo_ind_desc_cred = "0" 
            else: 
                novo_ind_desc_cred = "1" 
        else: 
            novo_ind_desc_cred = "1" 

        valor_antigo_ind = registro_m100.obter_campo(idx_ind_desc_cred)
        if valor_antigo_ind != novo_ind_desc_cred:
            registro_m100.definir_campo(idx_ind_desc_cred, novo_ind_desc_cred)
            campos_modificados_indices.append(idx_ind_desc_cred)

        # Lógica para SLD_CRED (idx_sld_cred_a_diferir)
        sld_cred_a_diferir = cred_disponivel - cred_utilizado
        novo_sld_cred_str = f"{sld_cred_a_diferir:.2f}".replace('.', ',')

        valor_antigo_sld = registro_m100.obter_campo(idx_sld_cred_a_diferir)
        if valor_antigo_sld != novo_sld_cred_str:
            registro_m100.definir_campo(idx_sld_cred_a_diferir, novo_sld_cred_str)
            campos_modificados_indices.append(idx_sld_cred_a_diferir)
        
        if campos_modificados_indices:
            print(f"Regra 'aplicar_logica_utilizacao_credito_m100' aplicada. Campos alterados: {campos_modificados_indices}")
        else:
            print("Regra 'aplicar_logica_utilizacao_credito_m100': Nenhuma alteração efetiva nos campos calculados.")
            
        return campos_modificados_indices

    except InvalidOperation:
        print(f"M100 (Lógica Uso): Erro de conversão de valor numérico. Verifique os campos VL_CRED_DISP e VL_CRED_DESC.")
        return None
    except Exception as e:
        print(f"Erro ao aplicar regra 'aplicar_logica_utilizacao_credito_m100': {e}")
        return None

def m100_usar_credito_total(registro_m100, todos_os_registros=None) -> list[int] | None:
    """
    Regra para M100: Configura o registro para utilizar o total do crédito disponível.
    - VL_CRED_DESC (idx 13) = VL_CRED_DISP (idx 11)
    - IND_DESC_CRED (idx 12) = "0"
    - SLD_CRED (idx 14) = "0,00"
    Retorna lista de índices de campos modificados, lista vazia se nada mudou, ou None em caso de erro.
    """
    campos_modificados_indices = []
    try:
        idx_vl_cred_disponivel = 11
        idx_ind_desc_cred = 12
        idx_vl_cred_desc = 13
        idx_sld_cred_a_diferir = 14

        vl_cred_disponivel_str = registro_m100.obter_campo(idx_vl_cred_disponivel)

        if vl_cred_disponivel_str is None:
            print("M100 (Usar Total): Campo VL_CRED_DISP não encontrado.")
            return None

        cred_disponivel = Decimal(vl_cred_disponivel_str.replace(',', '.'))

        # Definir VL_CRED_DESC para ser igual ao VL_CRED_DISP
        novo_vl_cred_desc_str = f"{cred_disponivel:.2f}".replace('.', ',')
        # Definir IND_DESC_CRED para "0"
        novo_ind_desc_cred = "0"
        # Definir SLD_CRED para "0,00"
        novo_sld_cred_a_diferir_str = "0,00"

        if registro_m100.obter_campo(idx_vl_cred_desc) != novo_vl_cred_desc_str:
            registro_m100.definir_campo(idx_vl_cred_desc, novo_vl_cred_desc_str)
            campos_modificados_indices.append(idx_vl_cred_desc)
        
        if registro_m100.obter_campo(idx_ind_desc_cred) != novo_ind_desc_cred:
            registro_m100.definir_campo(idx_ind_desc_cred, novo_ind_desc_cred)
            campos_modificados_indices.append(idx_ind_desc_cred)

        if registro_m100.obter_campo(idx_sld_cred_a_diferir) != novo_sld_cred_a_diferir_str:
            registro_m100.definir_campo(idx_sld_cred_a_diferir, novo_sld_cred_a_diferir_str)
            campos_modificados_indices.append(idx_sld_cred_a_diferir)

        if campos_modificados_indices:
            print(f"Regra M100 'Usar Crédito Total' aplicada. Campos alterados: {campos_modificados_indices}")
        else:
            print("Regra M100 'Usar Crédito Total': Nenhuma alteração necessária.")
            
        return campos_modificados_indices

    except InvalidOperation:
        print("M100 (Usar Total): Erro de conversão de valor numérico para VL_CRED_DISP.")
        return None
    except Exception as e:
        print(f"Erro ao aplicar regra 'M100 Usar Crédito Total': {e}")
        return None

# --- Dicionário de Regras Disponíveis ---
# Mapeia tipo_registro para uma lista de dicionários de regras.
# Cada dicionário de regra contém:
#   "nome_exibicao": O nome que aparecerá na GUI.
#   "funcao": A referência à função Python que executa a regra.
#   "descricao": Uma breve descrição da regra (para tooltips, por exemplo).

regras_disponiveis = {
    "M210": [
        {
            "nome_exibicao": "M210: Calcular Contribuição PIS",
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
        "nome_exibicao": "M100: Uso de Crédito (11 - 13)",
        "funcao": aplicar_logica_utilizacao_credito_m100,
        "descricao": "Calcula o Indicador de Uso e o Saldo a Diferir com base no Crédito Disponível e no Crédito Utilizado no período."
    }
)
regras_disponiveis["M100"].append(
    {
        "nome_exibicao": "M100: Usar Crédito Total (Zerar Saldo)",
        "funcao": m100_usar_credito_total,
        "descricao": "Define VL_CRED_DESC igual a VL_CRED_DISP, IND_DESC_CRED para '0' e SLD_CRED para '0,00'."
    }
)