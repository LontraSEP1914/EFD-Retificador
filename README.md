# EFD-Retificador

![Ícone do SPED]((https://trssistemas.com.br/wp-content/uploads/2020/11/sped-fiscal-343.png)) Uma ferramenta desktop desenvolvida em Python e PyQt6 para visualizar, editar e automatizar a retificação de arquivos da EFD Contribuições (SPED Fiscal). A aplicação permite que analistas fiscais manipulem os registros do arquivo TXT de forma intuitiva, apliquem regras de negócio pré-definidas e gerem o arquivo retificado com segurança.

Este projeto foi criado para resolver a necessidade de automação na análise e correção de créditos fiscais, reduzindo o tempo de análise em até 75%, como destacado no [meu portfólio](https://lontrasep1914.github.io/).

## ✨ Funcionalidades Principais

* **Visualização e Edição:** Carregue o arquivo `.txt` da EFD Contribuições e navegue pelos registros de forma estruturada.
* **Filtro Inteligente:** Filtre rapidamente os registros por tipo (ex: "M100", "M210") para encontrar as informações que precisa.
* **Editor de Campos Detalhado:** Selecione um registro e edite seus campos em um formulário claro, com descrições baseadas no leiaute oficial da EFD.
* **Automação de Regras:** Aplique regras de negócio com um clique para automatizar cálculos e preenchimentos, como:
    * **M100:** Calcular o saldo de crédito a diferir com base no valor utilizado.
    * **M210:** Recalcular o valor da contribuição apurada com base na base de cálculo e alíquota.
* **Geração Segura de Arquivo:** Salve as alterações em um novo arquivo `.txt`, mantendo o arquivo original intacto.
* **Interface Amigável:** Interface gráfica desenvolvida com PyQt6, pensada para a agilidade do usuário final.

## 🛠️ Tecnologias Utilizadas

* **Python:** Linguagem principal do projeto.
* **PyQt6:** Para a construção da interface gráfica desktop.
* **Estrutura Modular:** O código é organizado em `core` (lógica de negócio) e `gui` (interface), facilitando a manutenção.

## 🚀 Como Usar

1.  Clone o repositório.
2.  Instale as dependências: `pip install PyQt6`.
3.  Execute o arquivo `main.py` para iniciar a aplicação.
4.  Use o menu "Arquivo" > "Abrir EFD" para carregar seu arquivo `.txt`.
5.  Navegue, edite e aplique as regras de automação conforme necessário.
6.  Salve o resultado em "Arquivo" > "Salvar EFD Retificado".
