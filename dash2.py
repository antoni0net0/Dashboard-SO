import os
import platform
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import time

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

def get_process_info():
    processes = []
    total_time1 = get_total_cpu_time()
    time.sleep(0.1)
    total_time2 = get_total_cpu_time()
    total_time_diff = max(total_time2 - total_time1, 1)  # Evita divisão por zero
    
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f'/proc/{pid}/stat', 'r') as f:
                    data = f.read().split()
                    proc_name = data[1].strip('()')
                    utime, stime = int(data[13]), int(data[14])
                    process_time = utime + stime
                
                time.sleep(0.1)
                with open(f'/proc/{pid}/stat', 'r') as f:
                    data = f.read().split()
                    utime2, stime2 = int(data[13]), int(data[14])
                    process_time2 = utime2 + stime2
                    
                process_time_diff = process_time2 - process_time
                cpu_usage = max((process_time_diff / total_time_diff) * 100, 0)  # Garante valores válidos
                
                with open(f'/proc/{pid}/statm', 'r') as f:
                    memory_usage = int(f.read().split()[0]) * 4 / 1024
                
                processes.append({
                    "PID": int(pid),
                    "Nome": proc_name,
                    "CPU (%)": round(cpu_usage, 2),
                    "Memória (MB)": round(memory_usage, 2)
                })
            except (FileNotFoundError, IndexError, ValueError, ZeroDivisionError):
                continue
    return processes

def get_total_cpu_time():
    with open("/proc/stat", "r") as f:
        cpu_line = f.readline().split()
    return sum(map(int, cpu_line[1:]))

def get_cpu_usage():
    with open("/proc/stat", "r") as f:
        lines = f.readlines()
    cpu_line = lines[0]
    cpu_data = cpu_line.split()[1:]
    cpu_data = list(map(int, cpu_data))
    
    total = sum(cpu_data)
    idle = cpu_data[3]
    
    usage = 100 * (1 - idle / total)
    return round(usage, 2)

def get_memory_usage():
    with open("/proc/meminfo", "r") as f:
        lines = f.readlines()
    mem_total = int(lines[0].split()[1])
    mem_free = int(lines[1].split()[1])
    
    used_memory = mem_total - mem_free
    usage = (used_memory / mem_total) * 100
    return round(usage, 2)

def get_file_system_info():
    partitions = []
    with open("/proc/mounts", "r") as f:
        for line in f:
            parts = line.split()
            partitions.append({
                "Dispositivo": parts[0],
                "Ponto de Montagem": parts[1],
                "Tipo": parts[2]
            })
    return partitions

def list_directory(path):
    try:
        entries = []
        with os.scandir(path) as it:
            for entry in it:
                entries.append({
                    "Nome": entry.name,
                    "Tamanho (KB)": entry.stat().st_size // 1024,
                    "Permissões": oct(entry.stat().st_mode)[-3:]
                })
        return entries
    except PermissionError:
        return [{"Nome": "Permissão Negada", "Tamanho (KB)": "-", "Permissões": "-"}]

def get_open_files(pid):
    open_files = []
    try:
        for fd in os.listdir(f'/proc/{pid}/fd'):
            fd_path = os.readlink(f'/proc/{pid}/fd/{fd}')
            open_files.append(fd_path)
    except (FileNotFoundError, PermissionError):
        pass
    return open_files

# Layout do Dashboard
app.layout = html.Div([
    html.H1("Dashboard de Sistema e Processos", style={'text-align': 'center'}),

    # Abas principais
    dcc.Tabs([ 
        # Aba de sistema
        dcc.Tab(label="Sistema de Arquivos", children=[ 
            html.Div([ 
                html.H2("Partições e Uso do Sistema de Arquivos"),
                dash_table.DataTable(
                    id="file-system-table", 
                    columns=[ 
                        {"name": "Dispositivo", "id": "Dispositivo"},
                        {"name": "Ponto de Montagem", "id": "Ponto de Montagem"},
                        {"name": "Tipo", "id": "Tipo"}
                    ]
                )
            ]),
            html.Div([ 
                html.H2("Navegar na Árvore de Diretórios"),
                dcc.Input(id="directory-path", type="text", value="/", style={'width': '80%'}),
                html.Button("Listar", id="list-directory"),
                dash_table.DataTable(
                    id="directory-table",
                    columns=[ 
                        {"name": "Nome", "id": "Nome"},
                        {"name": "Tamanho (KB)", "id": "Tamanho (KB)"},
                        {"name": "Permissões", "id": "Permissões"}
                    ]
                )
            ])
        ]),

        # Aba de processos
        dcc.Tab(label="Processos", children=[ 
            html.Div([ 
                dash_table.DataTable(
                    id='process-table', 
                    columns=[ 
                        {'name': 'PID', 'id': 'PID'},
                        {'name': 'Nome', 'id': 'Nome'},
                        {'name': 'CPU (%)', 'id': 'CPU (%)'},
                        {'name': 'Memória (MB)', 'id': 'Memória (MB)'}
                    ],
                    style_table={'overflowY': 'auto'},
                    sort_action='native',  # Permite ordenação
                    sort_by=[{'column_id': 'PID', 'direction': 'asc'}]  # Ordenação inicial
                )
            ]),
            html.Div([ 
                html.H2("Arquivos Abertos pelo Processo"),
                dcc.Input(id="process-id", type="number", placeholder="Digite o PID"),
                html.Button("Listar Arquivos", id="list-open-files"),
                dash_table.DataTable(
                    id="open-files-table",
                    columns=[ 
                        {"name": "Arquivo Aberto", "id": "Arquivo Aberto"}
                    ]
                )
            ])
        ])
    ]), 
    
    # Gráficos
    html.Div([ 
        dcc.Graph(id="cpu-usage-graph"),
        dcc.Graph(id="memory-usage-graph")
    ]),

    # Intervalo para atualização
    dcc.Interval(id='update-interval', interval=5000, n_intervals=0)
])

# Callbacks
@app.callback(
    Output("file-system-table", "data"),
    Input("update-interval", "n_intervals")
)
def update_file_system_info(_):
    return get_file_system_info()

@app.callback(
    Output("directory-table", "data"),
    Input("list-directory", "n_clicks"),
    State("directory-path", "value")
)
def update_directory_table(_, path):
    return list_directory(path)

@app.callback(
    Output("open-files-table", "data"),
    Input("list-open-files", "n_clicks"),
    State("process-id", "value")
)
def update_open_files(_, pid):
    if pid is None:
        return []
    files = get_open_files(pid)
    return [{"Arquivo Aberto": f} for f in files]

@app.callback(
    Output("process-table", "data"),
    Input("update-interval", "n_intervals")
)
def update_process_table(_):
    return get_process_info()

@app.callback(
    Output("cpu-usage-graph", "figure"),
    Output("memory-usage-graph", "figure"),
    Input("update-interval", "n_intervals")
)
def update_graphs(_):
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()

    # Gráfico de uso de CPU
    cpu_fig = {
        'data': [go.Bar(x=["Uso de CPU"], y=[cpu_usage], name="CPU Usage")],
        'layout': go.Layout(
            title="Uso de CPU (%)",
            xaxis={'title': 'CPU'},
            yaxis={'title': 'Uso (%)'}
        )
    }

    # Gráfico de uso de Memória
    memory_fig = {
        'data': [go.Bar(x=["Uso de Memória"], y=[memory_usage], name="Memory Usage")],
        'layout': go.Layout(
            title="Uso de Memória (%)",
            xaxis={'title': 'Memória'},
            yaxis={'title': 'Uso (%)'}
            
        )
    }

    return cpu_fig, memory_fig

# Rodar o app
if __name__ == '__main__':
    app.run_server(debug=True)
