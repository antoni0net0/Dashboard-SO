import os
import platform
import psutil
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Inicializa o app Dash
app = dash.Dash(_name_)

# Função para coletar informações sobre o sistema operacional
def get_system_info():
    # Retorna um dicionário com as principais informações do sistema
    return {
        "Sistema Operacional": platform.system(),  # Nome do sistema operacional (ex: Windows, Linux)
        "Versão": platform.version(),  # Versão do sistema operacional
        "Arquitetura": platform.architecture()[0],  # Arquitetura do sistema (32-bit ou 64-bit)
        "Processador": platform.processor(),  # Nome do processador
        "Nome do Host": platform.node()  # Nome do computador (host)
    }

# Função para coletar informações de hardware (memória, CPU e disco)
def get_hardware_info():
    mem = psutil.virtual_memory()  # Obtém informações sobre a memória RAM
    disk = psutil.disk_usage('/')  # Obtém informações sobre o uso do disco rígido
    cpu_usage = psutil.cpu_percent(interval=0.5)  # Obtém o uso da CPU em percentual
    # Retorna um dicionário com os dados de uso de CPU, memória e disco
    return {
        "CPU Uso (%)": cpu_usage,  # Percentual de uso da CPU
        "Memória Total (GB)": round(mem.total / 1e9, 2),  # Memória total em GB
        "Memória Usada (GB)": round(mem.used / 1e9, 2),  # Memória usada em GB
        "Espaço Total Disco (GB)": round(disk.total / 1e9, 2),  # Espaço total do disco em GB
        "Espaço Usado Disco (GB)": round(disk.used / 1e9, 2)  # Espaço usado no disco em GB
    }

# Função para coletar informações de todos os processos em execução
def get_all_process_info():
    # Itera sobre todos os processos e retorna uma lista com informações sobre cada um
    return [
        {
            "PID": proc.info["pid"],  # ID do processo
            "Nome": proc.info["name"],  # Nome do processo
            "CPU (%)": proc.info["cpu_percent"],  # Percentual de uso da CPU
            "Memória (%)": proc.info["memory_percent"],  # Percentual de memória usada
        }
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"])  # Itera sobre os processos
    ]

# Layout do Dashboard (estrutura visual do app)
app.layout = html.Div([  # Container principal
    html.H1("Dashboard do Sistema Operacional", style={  # Título principal
        'text-align': 'center', 'color': '#ffffff', 'background-color': '#2A4D14',
        'font-family': 'Arial, sans-serif', 'font-size': '32px',
        'padding': '15px', 'border-radius': '8px', 'margin-bottom': '20px'
    }),

    # Informações Globais
    html.Div([
        html.H3("Informações do Sistema", style={'color': '#2A4D14', 'font-size': '24px'}),  # Subtítulo "Informações do Sistema"
        html.Ul(id='system-info', style={'color': '#000000', 'font-size': '18px'}),  # Lista para mostrar as informações do sistema
        html.H3("Informações de Hardware", style={'color': '#2A4D14', 'font-size': '24px'}),  # Subtítulo "Informações de Hardware"
        html.Ul(id='hardware-info', style={'color': '#000000', 'font-size': '18px'})  # Lista para mostrar as informações de hardware
    ], style={
        'background-color': '#A6CE39', 'padding': '20px',
        'border-radius': '8px', 'margin-bottom': '20px'
    }),

    # Gráficos
    html.Div([
        html.H3("Gráficos de Uso", style={'color': '#2A4D14', 'font-size': '24px'}),  # Subtítulo "Gráficos de Uso"
        html.Div([  # Container para os gráficos
            dcc.Graph(id='cpu-usage', style={'height': '300px', 'width': '50%'}),  # Gráfico de uso de CPU
            dcc.Graph(id='disk-usage', style={'height': '300px', 'width': '50%'})  # Gráfico de uso de disco
        ], style={'display': 'flex', 'gap': '10px', 'justify-content': 'center'})  # Alinha os gráficos lado a lado
    ], style={
        'background-color': '#A6CE39', 'padding': '20px',
        'border-radius': '8px', 'margin-bottom': '20px'
    }),

    # Selecione um Processo
    html.Div([
        html.H3("Selecione um Processo", style={'color': '#2A4D14', 'font-size': '24px'}),  # Subtítulo "Selecione um Processo"
        dcc.Dropdown(
            id='process-selector',  # Dropdown para selecionar o processo
            placeholder="Selecione um processo",  # Texto de instrução
            style={'width': '100%', 'padding': '10px', 'background-color': '#ffffff', 'border-radius': '5px'},
            options=[],  # Opções de processos (serão carregadas dinamicamente)
            value=None  # Valor inicial (nenhum processo selecionado)
        )
    ], style={
        'background-color': '#A6CE39', 'padding': '20px',
        'border-radius': '8px', 'margin-bottom': '20px'
    }),

    # Detalhes do Processo
    html.Div(id='process-details', style={  # Container para mostrar os detalhes do processo
        'color': '#000000', 'font-size': '18px', 'background-color': '#A6CE39',
        'padding': '20px', 'border-radius': '8px'
    }),

    # Intervalo de Atualização
    dcc.Interval(id='update-interval', interval=5000, n_intervals=0)  # Intervalo de atualização do dashboard (5 segundos)
], style={
    'background-color': '#CDE67D', 'padding': '30px',
    'font-family': 'Arial, sans-serif', 'min-height': '100vh'
})

# Callback para atualizar os dados do dashboard
@app.callback(
    [Output('system-info', 'children'),  # Atualiza a lista de informações do sistema
     Output('hardware-info', 'children'),  # Atualiza a lista de informações de hardware
     Output('process-selector', 'options'),  # Atualiza as opções do dropdown de processos
     Output('cpu-usage', 'figure'),  # Atualiza o gráfico de uso de CPU
     Output('disk-usage', 'figure')],  # Atualiza o gráfico de uso de disco
    [Input('update-interval', 'n_intervals')]  # O callback é ativado a cada 5 segundos
)
def update_dashboard(_):
    # Obtém as informações do sistema e hardware
    system_info = get_system_info()
    hardware_info = get_hardware_info()
    all_processes = get_all_process_info()

    # Converte as informações para listas HTML
    system_info_list = [html.Li(f"{key}: {value}") for key, value in system_info.items()]   
    hardware_info_list = [html.Li(f"{key}: {value}") for key, value in hardware_info.items()]
    process_options = [{'label': f"{proc['Nome']} (PID: {proc['PID']})", 'value': proc['PID']} for proc in all_processes]

    # Cria o gráfico de uso de CPU (indicador de gauge)
    cpu_figure = {
        'data': [
            go.Indicator(
                mode="gauge+number",  # Exibe o valor no gráfico de gauge
                value=hardware_info["CPU Uso (%)"],  # Valor do uso de CPU
                title={'text': "Uso da CPU (%)"},  # Título do gráfico
                gauge={'axis': {'range': [0, 100]},  # Intervalo do gráfico de gauge
                       'bar': {'color': "#4CAF50"}}  # Cor da barra do gráfico
            )
        ],
        'layout': go.Layout(paper_bgcolor="#ffffff", font={'color': '#2A4D14'})  # Layout do gráfico
    }

    # Calcula o percentual de uso do disco
    disk_usage_percent = (hardware_info["Espaço Usado Disco (GB)"] / hardware_info["Espaço Total Disco (GB)"]) * 100
    # Cria o gráfico de uso do disco (indicador de gauge)
    disk_figure = {
        'data': [
            go.Indicator(
                mode="gauge+number",  # Exibe o valor no gráfico de gauge
                value=disk_usage_percent,  # Valor do uso do disco      
                title={'text': "Uso do Disco (%)"},  # Título do gráfico
                gauge={'axis': {'range': [0, 100]},  # Intervalo do gráfico de gauge
                       'bar': {'color': "#4CAF50"}}  # Cor da barra do gráfico
            )
        ],
        'layout': go.Layout(paper_bgcolor="#ffffff", font={'color': '#2A4D14'})  # Layout do gráfico
    }

    # Retorna as informações para atualizar o layout
    return system_info_list, hardware_info_list, process_options, cpu_figure, disk_figure

# Callback para exibir os detalhes de um processo selecionado
@app.callback(
    Output('process-details', 'children'),  # Atualiza os detalhes do processo selecionado
    [Input('process-selector', 'value')]  # O callback é ativado quando um processo é selecionado
)
def update_process_details(pid):
    if pid:
        try:
            proc = psutil.Process(pid)  # Obtém o processo com o PID selecionado
            details = [
                html.Li(f"PID: {proc.pid}"),  # Mostra o PID
                html.Li(f"Nome: {proc.name()}"),  # Mostra o nome do processo
                html.Li(f"Status: {proc.status()}"),  # Mostra o status do processo
                html.Li(f"CPU: {proc.cpu_percent(interval=0.1)}%"),  # Mostra o uso de CPU do processo
                html.Li(f"Memória: {round(proc.memory_info().rss / 1e6, 2)} MB"),  # Mostra a memória usada pelo processo
            ]
            return html.Ul(details, style={'color': '#000000'})
        except psutil.NoSuchProcess:
            return "Processo não encontrado."  # Caso o processo tenha sido terminado
    return "Selecione um processo para ver os detalhes."  # Mensagem padrão caso nenhum processo tenha sido selecionado

# Executa o servidor
if _name_ == '_main_':
    psutil.cpu_percent(interval=None)  # Inicializa o cálculo do uso da CPU
    app.run_server(debug=True)  # Inicia o servidor Dash em modo de depuração