import os
import platform
import psutil
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Inicializar o app
app = dash.Dash(__name__)

# Funções para coletar informações do sistema
def get_system_info():
    return {
        "Sistema Operacional": platform.system(),
        "Versão": platform.version(),
        "Arquitetura": platform.architecture()[0],
        "Processador": platform.processor(),
        "Nome do Host": platform.node()
    }

def get_hardware_info():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "CPU Uso (%)": psutil.cpu_percent(interval=None),
        "Memória Total (GB)": round(mem.total / 1e9, 2),
        "Memória Usada (GB)": round(mem.used / 1e9, 2),
        "Espaço Total Disco (GB)": round(disk.total / 1e9, 2),
        "Espaço Usado Disco (GB)": round(disk.used / 1e9, 2)
    }

def get_all_process_info():
    return [
        {
            "PID": proc.info["pid"],
            "Nome": proc.info["name"],
            "CPU (%)": proc.info["cpu_percent"],
            "Memória (%)": proc.info["memory_percent"],
        }
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"])
    ]

# Layout do Dashboard
app.layout = html.Div([
    html.H1("Dashboard do Sistema Operacional", style={
        'text-align': 'center', 'color': '#FFFFFF', 'font-family': 'Arial, sans-serif',
        'font-size': '32px', 'margin': '20px 0', 'background-color': '#1E2A38', 'padding': '15px', 'border-radius': '8px'
    }),

    # Informações Globais
    html.Div([
        html.H3("Informações do Sistema", style={'color': '#FFFFFF', 'font-size': '24px', 'margin-bottom': '10px'}),
        html.Ul(id='system-info', style={'color': '#FFFFFF', 'font-size': '18px', 'list-style': 'none', 'padding': '0'}),
        html.Ul(id='hardware-info', style={'color': '#FFFFFF', 'font-size': '18px', 'list-style': 'none', 'padding': '0'}),
    ], style={'background-color': '#2E3B4E', 'padding': '20px', 'border-radius': '8px', 'margin-bottom': '20px'}),

    # Gráficos
    html.Div([
        html.H3("Gráficos de Uso", style={'color': '#FFFFFF', 'font-size': '24px', 'margin-bottom': '10px'}),
        html.Div([
            html.Div([
                dcc.Graph(id='cpu-usage', style={'height': '300px', 'width': '100%'}),
            ], style={'flex': '1', 'margin-right': '10px'}),
            html.Div([
                dcc.Graph(id='disk-usage', style={'height': '300px', 'width': '100%'}),
            ], style={'flex': '1', 'margin-left': '10px'}),
        ], style={'display': 'flex', 'justify-content': 'space-between'})
    ], style={'background-color': '#2E3B4E', 'padding': '20px', 'border-radius': '8px', 'margin-bottom': '20px'}),

    # Selecione um Processo
    html.Div([
        html.H3("Selecione um Processo", style={'color': '#FFFFFF', 'font-size': '24px', 'margin-bottom': '10px'}),
        dcc.Dropdown(
            id='process-selector',
            placeholder="Selecione um processo",
            style={'width': '100%', 'padding': '10px', 'backgroundColor': '#FFFFFF', 'border-radius': '5px'},
            options=[],
            value=None
        ),
    ], style={'background-color': '#2E3B4E', 'padding': '20px', 'border-radius': '8px', 'margin-bottom': '20px'}),

    # Aba de Detalhes do Processo
    html.Div(id='process-details', style={'color': '#FFFFFF', 'font-size': '18px', 'background-color': '#2E3B4E', 'padding': '20px', 'border-radius': '8px'}),

    # Intervalo de Atualização
    dcc.Interval(id='update-interval', interval=5000, n_intervals=0)
], style={'background-color': '#1E2A38', 'padding': '30px', 'font-family': 'Arial, sans-serif', 'min-height': '100vh'})

# Callbacks
@app.callback(
    [Output('system-info', 'children'),
     Output('hardware-info', 'children'),
     Output('process-selector', 'options'),
     Output('cpu-usage', 'figure'),
     Output('disk-usage', 'figure')],
    [Input('update-interval', 'n_intervals')]
)
def update_dashboard(_):
    # Informações do sistema
    system_info = get_system_info()
    system_info_list = [html.Li(f"{key}: {value}") for key, value in system_info.items()]

    # Informações de hardware
    hardware_info = get_hardware_info()
    hardware_info_list = [html.Li(f"{key}: {value}") for key, value in hardware_info.items()]

    # Obter processos
    all_processes = get_all_process_info()
    process_options = [{'label': f"{proc['Nome']} (PID: {proc['PID']})", 'value': proc['PID']} for proc in all_processes]

    # Gráfico de uso da CPU
    cpu_figure = {
        'data': [go.Indicator(
            mode="gauge+number",
            value=hardware_info["CPU Uso (%)"],
            title={'text': "Uso da CPU (%)"},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "green"}}
        )]
    }

    # Gráfico de uso do disco
    disk_usage_percent = (hardware_info["Espaço Usado Disco (GB)"] / hardware_info["Espaço Total Disco (GB)"]) * 100
    disk_figure = {
        'data': [go.Indicator(
            mode="gauge+number",
            value=disk_usage_percent,
            title={'text': "Uso do Disco (%)"},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "red"}}
        )]
    }

    return system_info_list, hardware_info_list, process_options, cpu_figure, disk_figure

@app.callback(
    Output('process-details', 'children'),
    [Input('process-selector', 'value')]
)
def update_process_details(pid):
    if pid:
        try:
            proc = psutil.Process(pid)
            details = [
                html.Li(f"PID: {proc.pid}"),
                html.Li(f"Nome: {proc.name()}"),
                html.Li(f"Status: {proc.status()}"),
                html.Li(f"CPU: {proc.cpu_percent(interval=0.1)}%"),
                html.Li(f"Memória: {round(proc.memory_info().rss / 1e6, 2)} MB"),
            ]
            return html.Ul(details, style={'color': '#FFFFFF'})
        except psutil.NoSuchProcess:
            return "Processo não encontrado."
    return "Selecione um processo para ver os detalhes."

# Executar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)