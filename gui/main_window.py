# gui/main_window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QListWidget, QListWidgetItem,
                             QLabel, QLineEdit, QMenuBar, QFormLayout,
                             QScrollArea, QMessageBox)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from functools import partial # Para conectar sinais com argumentos extras

from core.efd_parser import parse_efd_file
from core.efd_structures import RegistroEFD
from core.efd_generator import generate_efd_file

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_window_title = "Retificador EFD Contribuições"
        self.setWindowTitle(self.base_window_title)
        self.setGeometry(100, 100, 900, 700)

        self.registros_carregados: list[RegistroEFD] = []
        self.dados_modificados: bool = False # Flag para rastrear alterações

        self._setup_ui()

    def _set_dados_modificados(self, modificado: bool):
        """Atualiza o estado de modificação e o título da janela."""
        if self.dados_modificados == modificado:
            return # Sem mudança no estado
        
        self.dados_modificados = modificado
        if self.dados_modificados:
            self.setWindowTitle(f"{self.base_window_title}*")
        else:
            self.setWindowTitle(self.base_window_title)
        
        # Habilita/desabilita a ação de salvar com base nas modificações E se há dados
        self.salvar_action.setEnabled(self.dados_modificados and bool(self.registros_carregados))


    def _setup_ui(self):
        # --- Menu ---
        menu_bar = self.menuBar()
        arquivo_menu = menu_bar.addMenu("&Arquivo")

        abrir_action = QAction("&Abrir EFD (.txt)...", self)
        abrir_action.triggered.connect(self.abrir_arquivo_efd)
        arquivo_menu.addAction(abrir_action)

        self.salvar_action = QAction("&Salvar EFD Retificado...", self)
        self.salvar_action.triggered.connect(self.salvar_arquivo_efd)
        self.salvar_action.setEnabled(False) 
        arquivo_menu.addAction(self.salvar_action)

        arquivo_menu.addSeparator()

        sair_action = QAction("&Sair", self)
        sair_action.triggered.connect(self.close) # Usaremos closeEvent para verificar modificações
        arquivo_menu.addAction(sair_action)

        # --- Layout Principal ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_splitter_layout = QHBoxLayout(central_widget) 

        # --- Painel Esquerdo (Filtro e Lista de Registros) ---
        left_panel_widget = QWidget()
        left_panel_layout = QVBoxLayout(left_panel_widget)

        filtro_layout = QHBoxLayout()
        filtro_label = QLabel("Filtrar tipo:")
        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Ex: M200 (vazio p/ todos)")
        self.filtro_input.textChanged.connect(self.aplicar_filtro_registros)
        
        filtro_layout.addWidget(filtro_label)
        filtro_layout.addWidget(self.filtro_input)
        left_panel_layout.addLayout(filtro_layout)

        self.lista_registros_widget = QListWidget()
        self.lista_registros_widget.itemSelectionChanged.connect(self.exibir_detalhes_registro)
        left_panel_layout.addWidget(self.lista_registros_widget)
        
        main_splitter_layout.addWidget(left_panel_widget, 1)

        # --- Painel Direito (Detalhes do Registro) ---
        self.scroll_area_detalhes = QScrollArea()
        self.scroll_area_detalhes.setWidgetResizable(True)
        
        self.container_widget_detalhes = QWidget()
        self.detalhes_layout = QFormLayout(self.container_widget_detalhes)
        self.detalhes_layout.addRow(QLabel("Selecione um registro para ver os detalhes."))
        
        self.scroll_area_detalhes.setWidget(self.container_widget_detalhes)
        main_splitter_layout.addWidget(self.scroll_area_detalhes, 2)


    def abrir_arquivo_efd(self):
        if self.dados_modificados:
            resposta = QMessageBox.question(self, "Dados Modificados",
                                            "Você tem alterações não salvas. Deseja continuar e descartá-las?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                            QMessageBox.StandardButton.No)
            if resposta == QMessageBox.StandardButton.No:
                return

        filepath, _ = QFileDialog.getOpenFileName(
            self, "Abrir Arquivo EFD Contribuições", "",
            "Arquivos de Texto (*.txt);;Todos os Arquivos (*)"
        )
        if filepath:
            self.registros_carregados = parse_efd_file(filepath)
            self._set_dados_modificados(False) # Resetar flag de modificação ao abrir novo arquivo
            
            if self.registros_carregados:
                self.aplicar_filtro_registros()
                if self.lista_registros_widget.count() > 0:
                     self.lista_registros_widget.setCurrentRow(0)
            else:
                self.lista_registros_widget.clear()
                self.limpar_detalhes_registro()
                self.detalhes_layout.addRow(QLabel("Nenhum registro lido ou erro no parser."))
                QMessageBox.warning(self, "Erro de Leitura", "Nenhum registro foi lido do arquivo ou ocorreu um erro durante o parse.")
        else: # Caso o usuário cancele o QFileDialog
            pass


    def aplicar_filtro_registros(self):
        texto_filtro = self.filtro_input.text().strip().upper()
        self.lista_registros_widget.clear()
        # self.mapa_item_lista_para_indice_registro.clear() # Não precisamos mais deste mapa

        for idx, reg in enumerate(self.registros_carregados):
            if not texto_filtro or texto_filtro in reg.tipo_registro.upper():
                num_campos_dados = len(reg.campos) -1
                campos_preview = '|'.join(reg.campos[1:min(4, num_campos_dados + 1 )])
                display_text = f"{reg.tipo_registro} | {campos_preview}..." if campos_preview else reg.tipo_registro
                
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.ItemDataRole.UserRole, idx) 
                self.lista_registros_widget.addItem(list_item)
        
        self.limpar_detalhes_registro()
        if not self.registros_carregados:
             self.lista_registros_widget.addItem("Nenhum arquivo EFD carregado.")
             self.detalhes_layout.addRow(QLabel("Carregue um arquivo EFD para começar."))
        elif self.lista_registros_widget.count() == 0 and texto_filtro:
            self.lista_registros_widget.addItem(f"Nenhum registro encontrado para o filtro '{texto_filtro}'.")
            self.detalhes_layout.addRow(QLabel(f"Nenhum registro encontrado para o filtro '{texto_filtro}'."))
        elif self.lista_registros_widget.count() > 0 :
            # self.lista_registros_widget.setCurrentRow(0) # Movido para abrir_arquivo_efd para evitar re-seleção constante
            pass
        else:
            self.detalhes_layout.addRow(QLabel("Nenhum registro para exibir."))


    def limpar_detalhes_registro(self):
        while self.detalhes_layout.rowCount() > 0:
            self.detalhes_layout.removeRow(0)

    def exibir_detalhes_registro(self):
        self.limpar_detalhes_registro()
        
        selected_items = self.lista_registros_widget.selectedItems()
        if not selected_items:
            self.detalhes_layout.addRow(QLabel("Nenhum registro selecionado."))
            return

        list_item_selecionado = selected_items[0]
        indice_registro_original = list_item_selecionado.data(Qt.ItemDataRole.UserRole)

        if indice_registro_original is None:
             self.detalhes_layout.addRow(QLabel("Erro ao obter dados do registro."))
             return

        registro_selecionado = self.registros_carregados[indice_registro_original]

        self.detalhes_layout.addRow(QLabel(f"<b>Tipo do Registro: {registro_selecionado.tipo_registro}</b>"))

        for i, valor_campo in enumerate(registro_selecionado.campos):
            if i == 0: # Pula o campo de tipo de registro, já exibido
                continue 
            
            # Futuramente: label_texto = NOME_OFICIAL_DO_CAMPO (do Guia Prático)
            label_texto = f"Campo {i}:" 
            
            campo_edit = QLineEdit(valor_campo)
            # Conectar o sinal editingFinished para atualizar o modelo de dados
            # Usamos functools.partial para passar argumentos extras para o slot
            campo_edit.editingFinished.connect(
                partial(self.atualizar_campo_registro, 
                        indice_registro_original, 
                        i, # Este é o índice do campo na lista `registro_selecionado.campos`
                        campo_edit # Passamos o próprio QLineEdit para pegar o texto atualizado
                       )
            )
            self.detalhes_layout.addRow(label_texto, campo_edit)

        if not registro_selecionado.campos or len(registro_selecionado.campos) <=1:
             self.detalhes_layout.addRow(QLabel("Registro não possui campos de dados adicionais."))

    def atualizar_campo_registro(self, indice_do_registro_na_lista: int, indice_do_campo_no_registro: int, qlineedit_referencia: QLineEdit):
        """
        Chamado quando a edição de um QLineEdit de campo é finalizada.
        Atualiza o valor na estrutura de dados interna (self.registros_carregados).
        """
        novo_valor = qlineedit_referencia.text()
        
        # Pega o registro EFD da nossa lista principal
        registro_alvo = self.registros_carregados[indice_do_registro_na_lista]
        
        # Verifica se o valor realmente mudou para evitar marcar como modificado desnecessariamente
        valor_antigo = registro_alvo.obter_campo(indice_do_campo_no_registro)

        if valor_antigo != novo_valor:
            sucesso_definir = registro_alvo.definir_campo(indice_do_campo_no_registro, novo_valor)
            if sucesso_definir:
                print(f"Registro [{indice_do_registro_na_lista}] Campo [{indice_do_campo_no_registro}] atualizado para: '{novo_valor}'")
                self._set_dados_modificados(True)
            else:
                # Isso não deveria acontecer se o índice do campo for > 0
                print(f"Erro ao tentar definir campo [{indice_do_campo_no_registro}] do registro [{indice_do_registro_na_lista}]")
        else:
            # print(f"Campo [{indice_do_campo_no_registro}] não modificado.")
            pass

    def salvar_arquivo_efd(self):
        if not self.registros_carregados:
            QMessageBox.warning(self, "Nada para Salvar", "Nenhum dado carregado para salvar.")
            return
        # Removido: if not self.dados_modificados. O usuário pode querer salvar mesmo sem modificações (Salvar Como).
        # Se quiser manter a lógica de só salvar se modificado, descomente a verificação abaixo.
        # if not self.dados_modificados:
        #     QMessageBox.information(self, "Sem Modificações", "Não há alterações para salvar.")
        #     return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Salvar Arquivo EFD Retificado", "",
            "Arquivos de Texto (*.txt);;Todos os Arquivos (*)"
        )
        if filepath:
            try:
                # Chama a função do nosso novo módulo gerador
                sucesso = generate_efd_file(filepath, self.registros_carregados)
                
                if sucesso:
                    QMessageBox.information(self, "Sucesso", f"Arquivo EFD retificado salvo em:\n{filepath}")
                    self._set_dados_modificados(False) # Resetar flag após salvar com sucesso
                else:
                    QMessageBox.critical(self, "Erro ao Salvar", "Ocorreu um erro ao tentar salvar o arquivo.\nVerifique o console para mais detalhes.")
            except Exception as e: # Captura qualquer outra exceção inesperada do processo
                QMessageBox.critical(self, "Erro Crítico ao Salvar", f"Ocorreu um erro inesperado durante o salvamento:\n{e}")
                print(f"Erro crítico ao salvar arquivo em: {filepath} - {e}")


    def closeEvent(self, event):
        """Sobrescreve o evento de fechar a janela para verificar alterações não salvas."""
        if self.dados_modificados:
            resposta = QMessageBox.question(self, "Sair",
                                            "Você tem alterações não salvas. Deseja realmente sair e descartá-las?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                            QMessageBox.StandardButton.No)
            if resposta == QMessageBox.StandardButton.Yes:
                event.accept()  # Fecha a janela
            else:
                event.ignore()  # Não fecha a janela
        else:
            event.accept() # Fecha normalmente