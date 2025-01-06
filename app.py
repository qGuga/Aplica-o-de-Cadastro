import tkinter as tk
from tkinter import messagebox, simpledialog
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import logging
import json
import requests



# Configuração do logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

def verificar_conexao():
    try:
        requests.get('https://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Função para carregar dados locais
def carregar_dados_locais():
    if os.path.exists('dados_locais.json'):
        with open('dados_locais.json', 'r') as file:
            return json.load(file)
    return []

# Função para salvar dados locais
def salvar_dados_locais(dados):
    with open('dados_locais.json', 'w') as file:
        json.dump(dados, file)

# Função para sincronizar dados locais com o Google Sheets
def sincronizar_dados_locais(sheet):
    dados_locais = carregar_dados_locais()
    if dados_locais:
        try:
            for dados in dados_locais:
                sheet.append_row([dados['Nome'], dados['Bloco'], dados['Placa do Carro'], dados['Número do Apartamento']])
            os.remove('dados_locais.json')
            logging.info('Dados locais sincronizados com o Google Sheets.')
        except Exception as e:
            logging.error('Erro ao sincronizar dados locais:', exc_info=True)

# Configuração da API do Google Sheets
def configurar_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("Caminho da credencial.json", scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_url("link da tabela que vai ser vinculada")
        sheet = spreadsheet.sheet1

        # Configuração inicial: Adicionar cabeçalhos se necessário
        colunas_necessarias = ['Proprietário', 'Nome', 'Número do Apartamento', 'Bloco', 'Modelo (Carro)', 'Placa do Carro', 'Cor (Carro)']
        cabeçalhos = sheet.row_values(1)
        
        if not cabeçalhos:
            sheet.append_row(colunas_necessarias)
        else:
            for index, coluna in enumerate(colunas_necessarias):
                if index < len(cabeçalhos):
                    if cabeçalhos[index] != coluna:
                        sheet.update_cell(1, index + 1, coluna)
                else:
                    sheet.update_cell(1, index + 1, coluna)

        logging.info('Conexão com a planilha estabelecida com sucesso.')
        return sheet

    except Exception as e:
        logging.error('Erro ao configurar a API do Google Sheets:', exc_info=True)
        messagebox.showerror('Erro', 'Erro ao configurar a API do Google Sheets. Verifique as credenciais.')
        return None

# Configurações da aplicação
app = tk.Tk()
app.title('Sistema de Cadastramento Residencial')
app.geometry('400x600')

# Ajuste das cores
cor_de_fundo = '#282c34'
cor_texto = '#ffffff'
cor_botao = '#61afef'
cor_botao_texto = '#282c34'

app.configure(bg=cor_de_fundo)  # Cor de fundo

# Centralização dos widgets
app.grid_rowconfigure(0, weight=1)
app.grid_rowconfigure(1, weight=1)
app.grid_rowconfigure(2, weight=1)
app.grid_rowconfigure(3, weight=1)
app.grid_rowconfigure(4, weight=1)
app.grid_rowconfigure(5, weight=1)
app.grid_rowconfigure(6, weight=1)
app.grid_rowconfigure(7, weight=1)
app.grid_rowconfigure(8, weight=1)
app.grid_rowconfigure(9, weight=1)
app.grid_rowconfigure(10, weight=1)
app.grid_rowconfigure(11, weight=1)
app.grid_rowconfigure(12, weight=1)
app.grid_columnconfigure(0, weight=1)

# Adicionando variáveis
proprietario = tk.BooleanVar()


# Função para adicionar um residente e salvar em um arquivo HTML e no Google Sheets
def adicionar_residente():
    try:
        nome = entry_nome.get()
        bloco = entry_bloco.get()
        placa_carro = entry_placa_carro.get()
        numero_apartamento = entry_numero_apartamento.get()
        eh_proprietario = proprietario.get()
        modelo_carro = entry_modelo_carro.get()
        cor_carro = entry_cor_carro.get()

        if nome and bloco and placa_carro and numero_apartamento and modelo_carro and cor_carro:
            dados = {
                'Proprietário': 'Sim' if eh_proprietario else 'Não',
                'Nome': nome,
                'Número do Apartamento': numero_apartamento,
                'Bloco': bloco,
                'Modelo (Carro)': modelo_carro,
                'Placa do Carro': placa_carro,
                'Cor (Carro)': cor_carro
            }

            if verificar_conexao():
                sheet = configurar_sheets()
                if sheet:
                    # Verificar se o residente já está cadastrado
                    existentes = sheet.get_all_records()
                    for residente in existentes:
                        if (residente['Proprietário'] == dados['Proprietário'] and
                            residente['Nome'] == nome and
                            residente['Bloco'] == bloco and
                            residente['Placa do Carro'] == placa_carro and
                            residente['Número do Apartamento'] == numero_apartamento and
                            residente['Modelo (Carro)'] == modelo_carro and
                            residente['Cor (Carro)'] == cor_carro):
                            messagebox.showwarning('Erro', 'Residente já cadastrado!')
                            return

                    sheet.append_row([dados['Proprietário'], nome, numero_apartamento, bloco, modelo_carro, placa_carro, cor_carro])
                    logging.info('Residente adicionado ao Google Sheets: %s, %s, %s, %s, %s, %s, %s', dados['Proprietário'], nome, numero_apartamento, bloco, modelo_carro, placa_carro, cor_carro)
                    sincronizar_dados_locais(sheet)
                    messagebox.showinfo('Sucesso', 'Residente adicionado com sucesso!')

                else:
                    logging.warning('Falha na configuração do Google Sheets.')
                    messagebox.showerror('Erro', 'Erro ao acessar o Google Sheets. Verifique as credenciais.')
                    return
            else:
                # Salvar dados localmente
                dados_locais = carregar_dados_locais()
                dados_locais.append(dados)
                salvar_dados_locais(dados_locais)
                logging.info('Residente salvo localmente: %s, %s, %s, %s, %s, %s, %s', dados['Proprietário'], nome, numero_apartamento, bloco, modelo_carro, placa_carro, cor_carro)
                messagebox.showinfo('Sucesso', 'Residente adicionado com sucesso!')

            # Limpar campos de entrada
            entry_nome.delete(0, tk.END)
            entry_bloco.delete(0, tk.END)
            entry_placa_carro.delete(0, tk.END)
            entry_numero_apartamento.delete(0, tk.END)
            entry_modelo_carro.delete(0, tk.END)
            entry_cor_carro.delete(0, tk.END)
            proprietario.set(False)

        else:
            messagebox.showwarning('Atenção', 'Todos os campos são obrigatórios!')

    except Exception as e:
        logging.error('Erro ao adicionar residente:', exc_info=True)
        messagebox.showerror('Erro', 'Erro ao adicionar residente. Tente novamente.')


import tkinter.simpledialog as sd

import pandas as pd
from pandastable import Table, TableModel

# Função para visualizar a tabela do Google Sheets
def visualizar_tabela():
    try:
        sheet = configurar_sheets()
        if sheet:
            # Obter todos os dados
            dados = sheet.get_all_records()

            # Convertendo os dados para um DataFrame do pandas para facilitar a manipulação
            df = pd.DataFrame(dados)

            # Criando uma nova janela para exibir a tabela
            top = tk.Toplevel(app)
            top.title("Visualizar Tabela")
            top.configure(bg=cor_de_fundo)  # Definindo a cor de fundo da nova janela

            # Entrada para busca
            label_busca = tk.Label(top, text='Buscar Nome:', fg=cor_texto, bg=cor_de_fundo, font=('Helvetica', 14))
            label_busca.pack(pady=5)

            entry_busca = tk.Entry(top, bg=cor_botao_texto, fg=cor_texto, font=('Helvetica', 12))
            entry_busca.pack(pady=5)

            frame_tabela = tk.Frame(top, bg=cor_de_fundo)
            frame_tabela.pack(pady=20, fill='both', expand=True)

            # Usando pandastable para exibir os dados formatados em uma tabela
            tabela = Table(frame_tabela, dataframe=df, showtoolbar=False, showstatusbar=False)
            tabela.show()

            # Função para atualizar a visualização com base na busca
            def atualizar_visualizacao(event=None):
                busca = entry_busca.get().strip().lower()
                if busca:
                    dados_filtrados = df[df['Nome'].str.lower().str.contains(busca)]
                else:
                    dados_filtrados = df

                tabela.updateModel(TableModel(dataframe=dados_filtrados))
                tabela.redraw()

                # Redefinir o foco para a entrada de busca
                entry_busca.focus_set()

            entry_busca.bind("<KeyRelease>", atualizar_visualizacao)

            atualizar_visualizacao()  # Inicializa a visualização com todos os dados

        else:
            messagebox.showerror('Erro', 'Erro ao acessar o Google Sheets. Verifique as credenciais.')
            logging.error('Erro ao acessar o Google Sheets.')

    except Exception as e:
        logging.error('Erro ao visualizar tabela:', exc_info=True)
        messagebox.showerror('Erro', 'Erro ao visualizar tabela. Tente novamente.')

# Função para criar uma janela filha e coletar entradas com a mesma cor do software principal
def janela_filha(parent, title, labels):
    def on_ok():
        for label, entry in entries.items():
            entries[label] = entry.get()
        top.destroy()

    top = tk.Toplevel(parent)
    top.title(title)
    
    # Definindo as cores da janela filha
    top.configure(bg=cor_de_fundo)
    entries = {}

    for label_text in labels:
        label = tk.Label(top, text=label_text, fg=cor_texto, bg=cor_de_fundo, font=('Helvetica', 14))
        label.pack(pady=5)
        entry = tk.Entry(top, bg=cor_botao_texto, fg=cor_texto, font=('Helvetica', 12))
        entry.pack(pady=5)
        entries[label_text] = entry

    button_ok = tk.Button(top, text="OK", command=on_ok, bg=cor_botao, fg=cor_botao_texto, font=('Helvetica', 14))
    button_ok.pack(pady=20)

    parent.wait_window(top)

    return entries



# Função para remover residente
def remover_residente():
    try:
        # Solicitar os detalhes do residente a ser removido
        dados_residente = janela_filha(app, "Remover Residente", ["Nome Completo", "Número do Apartamento", "Bloco", "Modelo (Carro)", "Placa do Carro", "Cor (Carro)"])

        nome = dados_residente["Nome Completo"].strip()  # Remover espaços extras
        numero_apartamento = dados_residente["Número do Apartamento"].strip()
        bloco = dados_residente["Bloco"].strip()
        modelo_carro = dados_residente["Modelo (Carro)"].strip()
        placa_carro = dados_residente["Placa do Carro"].strip()
        cor_carro = dados_residente["Cor (Carro)"].strip()

        if not nome or not numero_apartamento or not bloco or not modelo_carro or not placa_carro or not cor_carro:
            logging.warning("Remoção cancelada ou campos não preenchidos corretamente.")
            return  # Se o usuário cancelar ou não digitar todos os detalhes, sai da função

        logging.info(f"Removendo residente: {nome}, Número do Apartamento: {numero_apartamento}, Bloco: {bloco}, Modelo: {modelo_carro}, Placa: {placa_carro}, Cor: {cor_carro}")

        # Conectar ao Google Sheets
        sheet = configurar_sheets()
        if sheet:
            # Obter todos os registros
            registros = sheet.get_all_records()
            linha_para_remover = None
            for i, registro in enumerate(registros, start=2):  # começando do índice 2 por causa do cabeçalho
                logging.debug(f"Verificando registro: {registro}")
                # Comparar dados sem considerar espaços extras
                if (registro['Nome'].strip().lower() == nome.lower() and
                    registro['Bloco'].strip().lower() == bloco.lower() and
                    registro['Modelo (Carro)'].strip().lower() == modelo_carro.lower() and
                    registro['Placa do Carro'].strip().lower() == placa_carro.lower() and
                    registro['Cor (Carro)'].strip().lower() == cor_carro.lower()):
                    linha_para_remover = i
                    break

            if linha_para_remover:
                logging.info(f"Linha para remover: {linha_para_remover}")
                sheet.delete_rows(linha_para_remover)  # Usando delete_rows em vez de delete_row
                logging.info('Residente removido do Google Sheets: %s', nome)
                messagebox.showinfo("Sucesso", f"Residente {nome} removido com sucesso!")
            else:
                logging.warning("Residente não encontrado.")
                messagebox.showwarning("Atenção", "Residente não encontrado.")

    except Exception as e:
        logging.error('Erro ao remover residente:', exc_info=True)
        messagebox.showerror('Erro', 'Erro ao remover residente. Tente novamente.')



# Interface gráfica

label_proprietario = tk.Label(app, text='Proprietário:', fg=cor_texto, bg=cor_de_fundo, font=('Helvetica', 14)) 
label_proprietario.grid(row=0, column=0, pady=5)

checkbox_proprietario = tk.Checkbutton(app, text='Sim', variable=proprietario, onvalue=True, offvalue=False, bg=cor_de_fundo, fg=cor_texto, selectcolor=cor_botao_texto, font=('Helvetica', 14)) 
checkbox_proprietario.grid(row=1, column=0, pady=5)

label_nome = tk.Label(app, text='Nome:', fg=cor_texto, bg=cor_de_fundo, font=('Helvetica', 14))
label_nome.grid(row=2, column=0, pady=5)

entry_nome = tk.Entry(app, bg=cor_botao_texto, fg=cor_texto, font=('Helvetica', 12))
entry_nome.grid(row=3, column=0, pady=5)

label_numero_apartamento = tk.Label(app, text='Número do Apartamento:', fg=cor_texto, bg=cor_de_fundo, font=('Helvetica', 14))
label_numero_apartamento.grid(row=4, column=0, pady=5)

entry_numero_apartamento = tk.Entry(app, bg=cor_botao_texto, fg=cor_texto, font=('Helvetica', 12))
entry_numero_apartamento.grid(row=5, column=0, pady=5)

label_bloco = tk.Label(app, text='Bloco:', fg=cor_texto, bg=cor_de_fundo, font=('Helvetica', 14))
label_bloco.grid(row=6, column=0, pady=5)

entry_bloco = tk.Entry(app, bg=cor_botao_texto, fg=cor_texto, font=('Helvetica', 12))
entry_bloco.grid(row=7, column=0, pady=5)

label_modelo_carro = tk.Label(app, text='Modelo (Carro):', fg=cor_texto, bg=cor_de_fundo, font=('Helvetica', 14))
label_modelo_carro.grid(row=8, column=0, pady=5)

entry_modelo_carro = tk.Entry(app, bg=cor_botao_texto, fg=cor_texto, font=('Helvetica', 12))
entry_modelo_carro.grid(row=9, column=0, pady=5)

label_placa_carro = tk.Label(app, text='Placa do Carro:', fg=cor_texto, bg=cor_de_fundo, font=('Helvetica', 14))
label_placa_carro.grid(row=10, column=0, pady=5)

entry_placa_carro = tk.Entry(app, bg=cor_botao_texto, fg=cor_texto, font=('Helvetica', 12))
entry_placa_carro.grid(row=11, column=0, pady=5)

label_cor_carro = tk.Label(app, text='Cor (Carro):', fg=cor_texto, bg=cor_de_fundo, font=('Helvetica', 14))
label_cor_carro.grid(row=12, column=0, pady=5)

entry_cor_carro = tk.Entry(app, bg=cor_botao_texto, fg=cor_texto, font=('Helvetica', 12))
entry_cor_carro.grid(row=13, column=0, pady=5)

button_adicionar = tk.Button(app, text='Adicionar Residente', command=adicionar_residente, bg=cor_botao, fg=cor_botao_texto, font=('Helvetica', 14))
button_adicionar.grid(row=14, column=0, pady=20)

button_remover = tk.Button(app, text='Remover Residente', command=remover_residente, bg=cor_botao, fg=cor_botao_texto, font=('Helvetica', 14))
button_remover.grid(row=15, column=0, pady=20)

button_visualizar = tk.Button(app, text='Visualizar Tabela', command=visualizar_tabela, bg=cor_botao, fg=cor_botao_texto, font=('Helvetica', 14)) 
button_visualizar.grid(row=16, column=0, pady=20)

# Iniciar a aplicação
app.mainloop()
