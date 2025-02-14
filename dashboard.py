import os
import platform
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import threading

# Model - Coleta e Processamento de Dados
class SystemModel:
    def __init__(self):
        self.processes = []
        self.cpu_usage = 0
        self.memory_usage = 0

    def get_system_info(self):
        return {
            "Sistema Operacional": platform.system(),
            "Versão": platform.version(),
            "Arquitetura": platform.architecture()[0],
            "Processador": platform.processor(),
            "Nome do Host": platform.node()
        }

    def get_process_info(self):
        processes_data = []
        for pid in os.listdir('/proc'):
            if pid.isdigit():
                try:
                    with open(f'/proc/{pid}/stat', 'r') as f:
                        data = f.read().split()
                        proc_name = data[1].strip('()')
                        cpu_usage = float(data[13]) + float(data[14])
                        memory_usage = int(data[22]) / 1e6
                    processes_data.append({
                        "PID": int(pid),
                        "Nome": proc_name,
                        "CPU (%)": round(cpu_usage, 2),
                        "Memória (MB)": round(memory_usage, 2)
                    })
                except (FileNotFoundError, IndexError, ValueError):
                    continue
        return processes_data

    def get_cpu_usage(self):
        with open("/proc/stat", "r") as f:
            lines = f.readlines()

        total_cpu_time = 0
        total_idle_time = 0

        # Iterar por cada linha 'cpu', representando cada núcleo
        for line in lines:
            if line.startswith('cpu'):
                cpu_data = line.split()[1:]
                cpu_data = list(map(int, cpu_data))

                total_cpu_time += sum(cpu_data)
                total_idle_time += cpu_data[3]  # tempo idle

        # Calcular o uso total de CPU
        total_usage = 100 * (1 - total_idle_time / total_cpu_time)
        return round(total_usage, 2)


    def get_memory_usage(self):
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
        mem_total = int(lines[0].split()[1])
        mem_free = int(lines[1].split()[1])

        used_memory = mem_total - mem_free
        usage = (used_memory / mem_total) * 100
        return round(usage, 2)

    def update_processes(self):
        self.processes = self.get_process_info()

    def update_cpu_usage(self):
        self.cpu_usage = self.get_cpu_usage()

    def update_memory_usage(self):
        self.memory_usage = self.get_memory_usage()


# Controller - Controla as Threads e a Atualização de Dados
class SystemController:
    def __init__(self, model):
        self.model = model

    def start_threads(self):
        threading.Thread(target=self.update_process_data, daemon=True).start()
        threading.Thread(target=self.update_cpu_data, daemon=True).start()
        threading.Thread(target=self.update_memory_data, daemon=True).start()

    def update_process_data(self):
        while True:
            self.model.update_processes()

    def update_cpu_data(self):
        while True:
            self.model.update_cpu_usage()

    def update_memory_data(self):
        while True:
            self.model.update_memory_usage()


# View - Interface do Usuário
class SystemView:
    def __init__(self, app, controller):
        self.app = app
        self.controller = controller
        self.layout()
        self.callbacks()

    def layout(self):
        self.app.layout = html.Div([
            html.H1("Dashboard de Processos", style={
                'text-align': 'center', 'color': '#2A3B0C', 'font-family': 'Arial, sans-serif',
                'font-size': '32px', 'margin': '20px 0', 'background-color': '#CDE67D', 'padding': '15px', 'border-radius': '8px'
            }),

            # Gráficos de uso de CPU e Memória
            html.Div([
                dcc.Graph(id='cpu-usage', style={'width': '40%', 'height': '300px', 'display': 'inline-block'}),
                dcc.Graph(id='memory-usage', style={'width': '40%', 'height': '300px', 'display': 'inline-block'})
            ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'}),

            # Filtro de Ordenação
            html.Div([
                html.Label("Ordenar por:", style={'font-size': '18px', 'margin-right': '10px'}),
                dcc.Dropdown(
                    id='sort-selector',
                    options=[
                        {'label': 'PID', 'value': 'PID'},
                        {'label': 'Uso de CPU (%)', 'value': 'CPU (%)'},
                        {'label': 'Uso de Memória (MB)', 'value': 'Memória (MB)'}
                    ],
                    value='PID',
                    style={'width': '50%', 'padding': '10px', 'border-radius': '5px'}
                )
            ], style={'margin-bottom': '20px'}),

            # Tabela de Processos
            html.Div([
                dash_table.DataTable(
                    id='process-table',
                    columns=[
                        {'name': 'PID', 'id': 'PID'},
                        {'name': 'Nome', 'id': 'Nome'},
                        {'name': 'CPU (%)', 'id': 'CPU (%)'},
                        {'name': 'Memória (MB)', 'id': 'Memória (MB)'}
                    ],
                    style_table={'height': '500px', 'overflowY': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '5px', 'font-family': 'Arial'},
                    style_header={
                        'backgroundColor': '#CDE67D',
                        'fontWeight': 'bold',
                        'border': '1px solid black'
                    },
                    style_data={
                        'border': '1px solid black'
                    },
                    page_action='none',
                    sort_action='native',  # Permite ordenar clicando no cabeçalho da tabela
                    sort_mode='single'     # Apenas uma coluna pode ser ordenada por vez
                )
            ], style={'background-color': '#CDE67D', 'padding': '20px', 'border-radius': '8px'}),

            # Intervalo de Atualização
            dcc.Interval(id='update-interval', interval=5000, n_intervals=0)
        ], style={'background-color': '#AEDE3C', 'padding': '30px', 'font-family': 'Arial, sans-serif', 'min-height': '100vh'})

    def callbacks(self):
        @self.app.callback(
            [Output('process-table', 'data'),
             Output('cpu-usage', 'figure'),
             Output('memory-usage', 'figure')],
            [Input('update-interval', 'n_intervals'),
             Input('sort-selector', 'value')]
        )
        def update_dashboard(_, sort_by):
            processes = self.controller.model.processes
            cpu_usage = self.controller.model.cpu_usage
            memory_usage = self.controller.model.memory_usage

            cpu_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=cpu_usage,
                title={'text': "Uso de CPU (%)"},
                gauge={'axis': {'range': [None, 100]}}
            ))

            memory_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=memory_usage,
                title={'text': "Uso de Memória (%)"},
                gauge={'axis': {'range': [None, 100]}}
            ))

            if sort_by:
                if sort_by == 'PID':
                    processes = sorted(processes, key=lambda x: x['PID'])
                elif sort_by == 'CPU (%)':
                    processes = sorted(processes, key=lambda x: x['CPU (%)'], reverse=True)
                elif sort_by == 'Memória (MB)':
                    processes = sorted(processes, key=lambda x: x['Memória (MB)'], reverse=True)

            return processes, cpu_fig, memory_fig


# Inicializando o sistema
app = dash.Dash(__name__)
model = SystemModel()
controller = SystemController(model)
view = SystemView(app, controller)

# Iniciar as threads
controller.start_threads()

# Executar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
