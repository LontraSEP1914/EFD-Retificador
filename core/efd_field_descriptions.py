# core/efd_field_descriptions.py

"""
Dicionário de dados para a EFD Contribuições.
Mapeia: TipoDeRegistro -> IndiceDoCampo -> {"nome": "NOME_CAMPO", "descr": "Descrição do Campo"}

Onde "IndiceDoCampo" é o índice na lista de campos (0-based) após o split da linha.
O campo de índice 0 é sempre o próprio tipo do registro.
"""

# 0: {"nome": "", "descr": ""}

efd_layout = {
    "0000": {
        0: {"nome": "REG", "descr": "Identificador do Registro"},
        1: {"nome": "COD_VER", "descr": "Código da versão do leiaute"},
        2: {"nome": "TIPO_ESCRIT", "descr": "Tipo de escrituração (0-Original; 1-Retificadora)"},
        3: {"nome": "IND_SIT_ESP", "descr": "Indicador de situação especial"},
        4: {"nome": "NUM_REC_ANTERIOR", "descr": "Número do recibo da escrituração anterior a ser retificada"},
        5: {"nome": "DT_INI", "descr": "Data de início do período da escrituração (DDMMAAAA)"},
        6: {"nome": "DT_FIN", "descr": "Data de fim do período da escrituração (DDMMAAAA)"},
        7: {"nome": "NOME", "descr": "Nome empresarial da pessoa jurídica"},
        8: {"nome": "CNPJ", "descr": "CNPJ da pessoa jurídica"},
        9: {"nome": "UF", "descr": "Unidade Federativa da pessoa jurídica"},
        10: {"nome": "COD_MUN", "descr": "Código do município do domicílio fiscal (Tabela IBGE)"},
        11: {"nome": "SUFRAMA", "descr": "Inscrição na Suframa"},
        12: {"nome": "IND_NAT_PJ", "descr": "Indicador da natureza da pessoa jurídica"},
        13: {"nome": "IND_ATIV", "descr": "Indicador do tipo de atividade preponderante"},
    },
    "0001": {
        0: {"nome": "REG", "descr": "Identificador do Registro"},
        1: {"nome": "IND_MOV", "descr": "Indicador de movimento (0-Bloco com dados; 1-Bloco sem dados)"},
    },
    "0110": { # Regime de Apuração da Contribuição
        0: {"nome": "REG", "descr": "Identificador do Registro"},
        1: {"nome": "COD_INC_TRIB", "descr": "Indicador do regime de incidência (1-Não Cumulativo; 2-Cumulativo; 3-Ambos)"},
        2: {"nome": "VL_REC_BRU_NC_TOT_PER", "descr": "Receita Bruta Não-Cumulativa Total no Período"},
        3: {"nome": "VL_REC_BRU_CUM_TOT_PER", "descr": "Receita Bruta Cumulativa Total no Período"},
        # ... (este registro tem mais campos)
    },
    # --- Bloco M (Exemplos) ---
    "M001": {
        0: {"nome": "REG", "descr": "Identificador do Registro"},
        1: {"nome": "IND_MOV", "descr": "Indicador de movimento (0-Bloco com dados; 1-Bloco sem dados)"},
    },
    "M100": {
        0: {"nome": "REG", "descr": "Identificador do Registro"},
        1: {"nome": "COD_CRED", "descr": "Código de Tipo de Crédito apurado no período"},
        2: {"nome": "IND_CRED_ORI", "descr": "Indicador de Crédito Oriundo (0 – Operações próprias, 1 – Evento de incorporação, cisão ou fusão.)"},
        3: {"nome": "VL_BC_PIS", "descr": "Valor da Base de Cálculo do Crédito"},
        4: {"nome": "ALIQ_PIS", "descr": "Alíquota do PIS/PASEP (em percentual)"},
        5: {"nome": "QUANT_BC_PIS", "descr": "Quantidade – Base de cálculo PIS"},
        6: {"nome": "ALIQ_PIS_QUANT", "descr": "Alíquota do PIS (em reais)"},
        7: {"nome": "VL_CRED", "descr": "Valor total do crédito apurado no período"},
        8: {"nome": "VL_AJUS_ACRES", "descr": "Valor total dos ajustes de acréscimo"},
        9: {"nome": "VL_AJUS_REDUC", "descr": "Valor total dos ajustes de redução"},
        10: {"nome": "VL_CRED_DIF", "descr": "Valor total do crédito diferido no período"},
        11: {"nome": "VL_CRED_DISP", "descr": "Valor Total do Crédito Disponível relativo ao Período (07 + 08 – 09 – 10)"},
        12: {"nome": "IND_DESC_CRED", "descr": "Indicador de opção de utilização do crédito disponível no período (0 - Uso Total, 1 - Uso Parcial)"},
        13: {"nome": "VL_CRED_DESC", "descr": "Valor do Crédito disponível, descontado da contribuição apurada no próprio período"},
        14: {"nome": "SLD_CRED", "descr": "Saldo de créditos a utilizar em períodos futuros (11 – 13)"},
    },
    "M200": { # Consolidação da Contribuição para o PIS/Pasep do Período
        0: {"nome": "REG", "descr": "Identificador do Registro"},
        1: {"nome": "VL_TOT_CONT_NC_PER", "descr": "Valor Total da Contribuição Não Cumulativa do Período (PIS)"},
        2: {"nome": "VL_TOT_CRED_DESC_PER", "descr": "Valor Total do Crédito Descontado no Período (PIS)"},
        3: {"nome": "VL_TOT_CRED_DESC_ANT_PER", "descr": "Valor Total do Crédito Descontado em Período Anterior (PIS)"},
        4: {"nome": "VL_TOT_CONT_NC_DEV", "descr": "Valor Total da Contribuição Não Cumulativa Devolvida no Período (PIS)"},
        5: {"nome": "VL_RET_NC", "descr": "Valor das Retenções na Fonte Não Cumulativas (PIS)"},
        # ... (este registro tem muitos campos)
    },
    "M210": { # Detalhamento da Contribuição para PIS/Pasep
        0: {"nome": "REG", "descr": "Identificador do Registro"},
        1: {"nome": "COD_CONT", "descr": "Código da Contribuição Social (conforme Tabela 4.3.5)"},
        2: {"nome": "VL_REC_BRT", "descr": "Valor da Receita Bruta"},
        3: {"nome": "VL_BC_CONT", "descr": "Valor da Base de Cálculo da Contribuição"},
        4: {"nome": "ALIQ_PIS", "descr": "Alíquota do PIS/Pasep (em percentual)"},
        5: {"nome": "VL_CONT_APUR", "descr": "Valor da Contribuição Apurada"},
        6: {"nome": "VL_CRED_PIS", "descr": "Valor do Crédito de PIS/Pasep a Descontar"},
        # ...
    },
    # --- Bloco 1 (Exemplos) ---
    "1001": {
        0: {"nome": "REG", "descr": "Identificador do Registro"},
        1: {"nome": "IND_MOV", "descr": "Indicador de movimento (0-Bloco com dados; 1-Bloco sem dados)"},
    },
    "1900": { # Consolidação dos Documentos Emitidos por ECF (PIS/Pasep e Cofins)
        0: {"nome": "REG", "descr": "Identificador do Registro"},
        1: {"nome": "CNPJ", "descr": "CNPJ do estabelecimento"},
        2: {"nome": "COD_MOD", "descr": "Código do modelo do documento fiscal (02, 2D)"},
        3: {"nome": "SER", "descr": "Série do documento fiscal"},
        4: {"nome": "SUB_SER", "descr": "Subsérie do documento fiscal"},
        # ...
    }
    # Adicione mais registros e campos conforme necessário
}