# main.py

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow  

COR_LARANJA_PRINCIPAL = "#dd9646"
COR_LARANJA_CLARO_BEGE = "#faf0d9" 
COR_TEXTO_ESCOLHIDA = "#bf8a59"    
COR_FUNDO_JANELA = "#fcf5e5"

COR_TEXTO_PADRAO_ESCURO = "#504A40" # Um marrom/cinza escuro para melhor contraste de texto
COR_BRANCA_TEXTO_BOTAO = "white"
COR_BORDA_LARANJA_ESCURA = "#c98235" # Um pouco mais escura que a principal para bordas/pressed

COR_CINZA_DESABILITADO_FUNDO = "#E0E0E0" # Um cinza claro para fundo de item desabilitado
COR_CINZA_DESABILITADO_TEXTO = "#A0A0A0" # Um cinza médio para texto de item desabilitado
COR_CINZA_DESABILITADO_BORDA = "#C0C0C0"

SPED_STYLE_SHEET = f"""
    QMainWindow {{
        background-color: {COR_FUNDO_JANELA};
    }}
    QWidget {{ /* Define uma cor de texto padrão para a maioria dos widgets */
        color: {COR_TEXTO_PADRAO_ESCURO}; 
    }}
    QPushButton {{
        background-color: {COR_LARANJA_PRINCIPAL};
        color: {COR_BRANCA_TEXTO_BOTAO};
        border: 1px solid {COR_BORDA_LARANJA_ESCURA};
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COR_LARANJA_CLARO_BEGE}; /* Teste com seu laranja claro */
        color: {COR_LARANJA_PRINCIPAL}; /* Texto do botão muda para o laranja principal */
        border-color: {COR_LARANJA_PRINCIPAL};
    }}
    QPushButton:pressed {{
        background-color: {COR_BORDA_LARANJA_ESCURA};
    }}
    QPushButton:disabled {{
    background-color: #cccccc; /* Um cinza para indicar desabilitado */
    color: #888888;
    border-color: #aaaaaa;
    }}
    QLineEdit, QComboBox, QListWidget {{
        border: 1px solid {COR_LARANJA_PRINCIPAL};
        padding: 4px;
        border-radius: 4px;
        background-color: white; /* Fundo branco para boa legibilidade do texto digitado */
        color: {COR_TEXTO_PADRAO_ESCURO}; /* Texto dentro dos inputs */
    }}
    /* Destaque para QLineEdit focado, se desejado */
    QLineEdit:focus {{
        border: 1px solid {COR_BORDA_LARANJA_ESCURA};
        /* background-color: {COR_LARANJA_CLARO_BEGE}; */ /* Opcional: fundo ao focar */
    }}
    QListWidget::item:selected {{
        background-color: {COR_LARANJA_PRINCIPAL}; 
        color: {COR_BRANCA_TEXTO_BOTAO};
    }}
    QListWidget::item:hover {{
        background-color: {COR_LARANJA_CLARO_BEGE};
        color: {COR_TEXTO_PADRAO_ESCURO};
    }}
    QLabel {{
        color: {COR_TEXTO_ESCOLHIDA}; /* Usando a cor de texto que você escolheu para QLabels */
    }}
    /* Para os QLabels que são 'títulos' nos QFormLayout (como nomes de campo) */
    /* Precisamos de uma forma de identificar esses QLabels. Se eles tiverem um objectName, ou se pudermos
       estilizar todos os QLabels dentro de um QScrollArea específico, ou todos os QLabels que são
       o primeiro widget em uma linha de QFormLayout.
       Por enquanto, vou deixar uma regra genérica, mas podemos refinar. */
    QFormLayout > QLabel {{ /* Tentativa de pegar QLabels diretamente no QFormLayout */
        font-weight: bold;
        color: {COR_LARANJA_PRINCIPAL}; /* Dando destaque com o laranja principal */
    }}
    /* Título do registro (QLabel com rich text) - pode precisar de um objectName para estilizar especificamente */
    /* Supondo que você dê um objectName="tituloRegistroLabel" ao QLabel do tipo de registro */
    QLabel#tituloRegistroLabel {{
        font-weight: bold;
        color: {COR_LARANJA_PRINCIPAL};
        /* padding-bottom: 5px; */ /* Exemplo de espaçamento */
    }}
    QMenuBar {{
        background-color: {COR_FUNDO_JANELA}; /* Ou um cinza bem claro #E5E5E5 */
        color: {COR_TEXTO_PADRAO_ESCURO};
        /* spacing: 5px; */ /* Espaçamento entre itens do menu bar, se desejado */
    }}
    QMenuBar::item {{
        background-color: transparent;
        padding: 4px 8px; /* Ajuste o padding para um bom visual */
        /* border-radius: 4px; */ /* Se quiser cantos arredondados para o item selecionado */
    }}
    QMenuBar::item:selected {{ /* Quando o mouse está sobre o item do menu bar (antes de clicar) ou quando o menu está aberto */
        background-color: {COR_LARANJA_PRINCIPAL};
        color: {COR_BRANCA_TEXTO_BOTAO};
    }}
    QMenuBar::item:pressed {{ /* Quando o item do menu bar é clicado para abrir o menu */
        background-color: {COR_BORDA_LARANJA_ESCURA};
        color: {COR_BRANCA_TEXTO_BOTAO};
    }}
    QMenuBar::item:disabled {{ /* Para um menu de topo se ele for desabilitado */
        color: {COR_CINZA_DESABILITADO_TEXTO};
        background-color: transparent; /* Ou um cinza muito sutil se preferir */
    }}
    QMenu {{
        background-color: white; 
        border: 1px solid {COR_BORDA_LARANJA_ESCURA}; /* Borda ao redor do menu dropdown */
        color: {COR_TEXTO_PADRAO_ESCURO};
        padding: 4px; /* Espaçamento interno do menu */
    }}
    QMenu::item {{
        padding: 4px 20px 4px 20px; /* Top, Right, Bottom, Left padding para itens de menu */
        /* min-width: 120px; */ /* Largura mínima se necessário */
    }}
    QMenu::item:selected {{ /* Quando o mouse está sobre um item no menu dropdown */
        background-color: {COR_LARANJA_PRINCIPAL};
        color: {COR_BRANCA_TEXTO_BOTAO};
    }}
    QMenu::item:disabled {{ /* Para uma ação desabilitada dentro de um menu dropdown */
        color: {COR_CINZA_DESABILITADO_TEXTO};
        background-color: transparent; /* Ou um cinza muito sutil se preferir */
        /* font-style: italic; */ /* Opcional: Estilo itálico para desabilitado */
    }}
    QMenu::separator {{
        height: 1px;
        background: {COR_CINZA_DESABILITADO_BORDA};
        margin-left: 5px;
        margin-right: 5px;
    }}
    QComboBox:disabled {{
    background-color: #eeeeee;
    border-color: #cccccc;
    color: #888888; /* Cor do placeholder text quando desabilitado */
    }}

"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(SPED_STYLE_SHEET)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())