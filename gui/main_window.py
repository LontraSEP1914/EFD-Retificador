# gui/main_window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QListWidget, QListWidgetItem,
                             QLabel, QLineEdit, QMenuBar, QFormLayout,
                             QScrollArea, QMessageBox, QComboBox)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QTimer
from functools import partial # Para conectar sinais com argumentos extras

from core.efd_parser import parse_efd_file
from core.efd_structures import RegistroEFD
from core.efd_generator import generate_efd_file
from core.efd_field_descriptions import efd_layout
from core.efd_record_automations import regras_disponiveis

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_window_title = "Retificador EFD Contribuições"
        self.setWindowTitle(self.base_window_title)
        self.setGeometry(100, 100, 900, 700)
        self.efd_layout = efd_layout
        self.regras_disponiveis_para_registro = regras_disponiveis # Carrega as definições de regras
        self.combo_regras_automacao = QComboBox()
        self.btn_aplicar_regra = QPushButton("Aplicar Regra")

        self.registros_carregados: list[RegistroEFD] = []
        self.dados_modificados: bool = False # Flag para rastrear alterações
        self.mapa_campos_widgets: dict[int, QLineEdit] = {} 

        self._setup_ui()
    
    # Método para destacar
    def _destacar_campo_temporariamente(self, qlineedit_widget: QLineEdit, duracao_ms: int = 1500, cor: str = "#ccffcc"): # Verde claro
        if qlineedit_widget:
            try:
                folha_estilo_original = qlineedit_widget.styleSheet()
                # Define um nome de objeto para o widget para que o timer possa encontrá-lo
                # e verificar se é o mesmo widget, caso a interface seja recriada rapidamente.
                # Usaremos o objectName para tentar tornar a restauração mais robusta.
                # No entanto, a complexidade de garantir que o widget não foi recriado é alta.
                # A abordagem mais simples é aceitar que se a UI for recriada, o destaque pode se perder
                # ou ser aplicado a um novo widget no mesmo local.
                # Para esta versão, a função de restauração capturará a folha_estilo_original.

                qlineedit_widget.setStyleSheet(f"background-color: {cor};")
                
                def restaurar_estilo():
                    # Tenta restaurar o estilo original.
                    # É importante verificar se o widget ainda existe.
                    try:
                        if qlineedit_widget: # Verifica se a referência ao widget ainda é válida
                             # Apenas restaura se o estilo atual ainda é o de destaque
                             # (evita sobrescrever um novo estilo aplicado por outra ação)
                            if qlineedit_widget.styleSheet() == f"background-color: {cor};":
                                qlineedit_widget.setStyleSheet(folha_estilo_original)
                    except RuntimeError: # Ocorre se o widget C++ subjacente foi excluído
                        pass # Widget não existe mais, nada a fazer

                QTimer.singleShot(duracao_ms, restaurar_estilo)
            except RuntimeError: 
                print(f"Aviso: Tentativa de destacar widget que pode não existir mais.")

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
        # self.scroll_area_detalhes = QScrollArea()
        # self.scroll_area_detalhes.setWidgetResizable(True)
        
        # self.container_widget_detalhes = QWidget()
        # self.detalhes_layout = QFormLayout(self.container_widget_detalhes)
        # self.detalhes_layout.addRow(QLabel("Selecione um registro para ver os detalhes."))
        
        # self.scroll_area_detalhes.setWidget(self.container_widget_detalhes)
        # main_splitter_layout.addWidget(self.scroll_area_detalhes, 2)  

        right_panel_container_widget = QWidget()
        right_panel_v_layout = QVBoxLayout(right_panel_container_widget)

        # Layout para Automação de Regras
        automacao_layout = QHBoxLayout()
        automacao_layout.addWidget(QLabel("Automação:"))
        self.combo_regras_automacao.setPlaceholderText("Nenhuma regra para este tipo.")
        self.combo_regras_automacao.setEnabled(False)
        automacao_layout.addWidget(self.combo_regras_automacao, 1) # Stretch factor

        self.btn_aplicar_regra.setEnabled(False)
        self.btn_aplicar_regra.clicked.connect(self.aplicar_regra_selecionada)
        automacao_layout.addWidget(self.btn_aplicar_regra)

        right_panel_v_layout.addLayout(automacao_layout) # Adiciona o layout de automação

        # ScrollArea para Detalhes do Registro (como antes)
        self.scroll_area_detalhes = QScrollArea()
        self.scroll_area_detalhes.setWidgetResizable(True)

        self.container_widget_detalhes = QWidget() 
        self.detalhes_layout = QFormLayout(self.container_widget_detalhes) 
        self.detalhes_layout.addRow(QLabel("Selecione um registro para ver os detalhes."))

        self.scroll_area_detalhes.setWidget(self.container_widget_detalhes)
        right_panel_v_layout.addWidget(self.scroll_area_detalhes) # Adiciona a área de scroll com os detalhes

        main_splitter_layout.addWidget(right_panel_container_widget, 2) # Adiciona o container do painel direito ao splitter


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
        # Limpar e desabilitar combo de regras também
        self.combo_regras_automacao.clear()
        self.combo_regras_automacao.setEnabled(False)
        self.combo_regras_automacao.setPlaceholderText("Selecione uma regra...")
        self.btn_aplicar_regra.setEnabled(False)

    def exibir_detalhes_registro(self):
        self.limpar_detalhes_registro()
        self.mapa_campos_widgets.clear()
        
        selected_items = self.lista_registros_widget.selectedItems()
        if not selected_items:
            self.detalhes_layout.addRow(QLabel("Nenhum registro selecionado."))
            # Limpar e desabilitar combo de regras se nenhum registro selecionado
            self.combo_regras_automacao.clear()
            self.combo_regras_automacao.setEnabled(False)
            self.btn_aplicar_regra.setEnabled(False)
            self.combo_regras_automacao.setPlaceholderText("Selecione um registro...")
            return

        list_item_selecionado = selected_items[0]
        indice_registro_original = list_item_selecionado.data(Qt.ItemDataRole.UserRole)

        if indice_registro_original is None or not (0 <= indice_registro_original < len(self.registros_carregados)):
             self.detalhes_layout.addRow(QLabel("Erro ao obter dados do registro."))
             return

        registro_selecionado = self.registros_carregados[indice_registro_original]

        self.detalhes_layout.addRow(QLabel(f"<b>Tipo do Registro: {registro_selecionado.tipo_registro}</b>"))

        for i, valor_campo in enumerate(registro_selecionado.campos):
            if i == 0: # Pula o campo de tipo de registro, já exibido
                continue 
            
            # Buscar informações do campo no nosso dicionário de dados
            info_campo = self.efd_layout.get(registro_selecionado.tipo_registro, {}).get(i)

            label_texto_descritivo: str
            tooltip_texto: str = ""

            if info_campo and info_campo.get("nome"):
                # Usar o nome oficial do campo e o índice para clareza
                label_texto_descritivo = f"{info_campo['nome']} (Índice {i}):" 
                tooltip_texto = info_campo.get('descr', '') # Pega a descrição para o tooltip
            else:
                label_texto_descritivo = f"Campo {i} (Nome Desconhecido):" # Fallback

            campo_label_widget = QLabel(label_texto_descritivo)
            if tooltip_texto:
                campo_label_widget.setToolTip(tooltip_texto)

            campo_edit = QLineEdit(valor_campo)
            if tooltip_texto: # Adicionar tooltip ao QLineEdit também pode ser útil
                campo_edit.setToolTip(f"{tooltip_texto}\nValor atual: {valor_campo}")

            self.mapa_campos_widgets[i] = campo_edit

            campo_edit.editingFinished.connect(
                partial(self.atualizar_campo_registro, 
                        indice_registro_original, 
                        i, 
                        campo_edit
                    )
            )
            # Adiciona o QLabel e o QLineEdit ao layout de formulário
            self.detalhes_layout.addRow(campo_label_widget, campo_edit)
            # Popular ComboBox de Regras de Automação
            self.combo_regras_automacao.clear()
            self.combo_regras_automacao.setEnabled(False)
            self.btn_aplicar_regra.setEnabled(False)

            if registro_selecionado: # Verifica se há um registro selecionado
                regras_para_tipo = self.regras_disponiveis_para_registro.get(registro_selecionado.tipo_registro, [])
                if regras_para_tipo:
                    self.combo_regras_automacao.setPlaceholderText("Selecione uma regra...")
                    for i, regra_info in enumerate(regras_para_tipo):
                        self.combo_regras_automacao.addItem(regra_info["nome_exibicao"], userData=regra_info) # Armazena todo o dict da regra
                        descricao_tooltip = regra_info.get("descricao", "")
                        if descricao_tooltip:
                            # 'i' aqui é o índice do item que acabamos de adicionar NO CONTEXTO DESTE LOOP DE POPULAÇÃO.
                            # Se o combo já tivesse itens antes de clear(), 'i' não seria o índice global correto.
                            # Mas como fazemos clear() antes, 'i' corresponde ao índice do item adicionado.
                            self.combo_regras_automacao.setItemData(i, descricao_tooltip, Qt.ItemDataRole.ToolTipRole)
                    
                    self.combo_regras_automacao.setEnabled(True)
                    self.btn_aplicar_regra.setEnabled(True)
                else:
                    self.combo_regras_automacao.setPlaceholderText("Nenhuma regra para este tipo.")

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
                if indice_do_campo_no_registro in self.mapa_campos_widgets:
                    widget_do_campo = self.mapa_campos_widgets[indice_do_campo_no_registro]
                    # Certificar-se de que o widget na tela é o mesmo que foi passado (qlineedit_referencia)
                    # Isso é uma segurança extra, pois o mapa é recriado ao exibir detalhes.
                    # Se o widget que disparou 'editingFinished' é o mesmo que está no mapa para esse índice, destaque-o.
                    if widget_do_campo is qlineedit_referencia:
                         self._destacar_campo_temporariamente(widget_do_campo)
                    else:
                        # Isso pode acontecer se a exibição de detalhes foi recarregada entre a edição e o fim da edição,
                        # ou se o mapa de alguma forma ficou dessincronizado. Pouco provável com editingFinished.
                        print(f"Aviso: Widget para campo {indice_do_campo_no_registro} no mapa é diferente do widget editado.")
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
    # Adicionar este novo método à classe MainWindow

    def aplicar_regra_selecionada(self):
        selected_items_registro = self.lista_registros_widget.selectedItems()
        if not selected_items_registro:
            QMessageBox.warning(self, "Atenção", "Nenhum registro selecionado para aplicar a regra.")
            return

        indice_combo_regra = self.combo_regras_automacao.currentIndex()
        if indice_combo_regra < 0: # Nenhum item selecionado ou placeholder
            QMessageBox.warning(self, "Atenção", "Nenhuma regra de automação selecionada.")
            return

        regra_data = self.combo_regras_automacao.currentData() # Recupera o dict da regra
        if not regra_data or "funcao" not in regra_data:
            QMessageBox.critical(self, "Erro", "Definição da regra inválida ou não encontrada.")
            return

        funcao_regra = regra_data["funcao"]

        # Obter o objeto RegistroEFD que está selecionado na lista principal
        list_item_selecionado_na_lista_principal = selected_items_registro[0]
        indice_registro_original = list_item_selecionado_na_lista_principal.data(Qt.ItemDataRole.UserRole)
        registro_efd_alvo = self.registros_carregados[indice_registro_original]

        # Chamar a função da regra
        # Passamos todos_os_registros caso a regra precise deles (opcional para a função da regra)
        modificado = funcao_regra(registro_efd_alvo, self.registros_carregados) 

        if modificado:
            self._set_dados_modificados(True)
            # Reexibir os detalhes do registro para refletir as mudanças
            # Isso é crucial para que os QLineEdits sejam atualizados.
            # Guardar a seleção atual da lista de registros para restaurá-la, se necessário,
            # pois exibir_detalhes_registro pode ser chamado por itemSelectionChanged e limpar a seleção.
            current_list_row = self.lista_registros_widget.currentRow()
            self.exibir_detalhes_registro() # Atualiza os QLineEdits
            if current_list_row != -1: # Restaura a seleção se foi perdida
                self.lista_registros_widget.setCurrentRow(current_list_row)
            for idx_campo_alterado in modificado:
                if idx_campo_alterado in self.mapa_campos_widgets:
                    self._destacar_campo_temporariamente(self.mapa_campos_widgets[idx_campo_alterado])
            QMessageBox.information(self, "Regra Aplicada", f"A regra '{regra_data['nome_exibicao']}' foi aplicada com sucesso.")
        else:
            # Se não modificou, pode ser por erro na regra (ver console) ou porque não havia o que mudar
            QMessageBox.information(self, "Regra Aplicada", f"A regra '{regra_data['nome_exibicao']}' foi processada, mas não resultou em alterações no registro ou encontrou um problema (verifique o console).")