import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Inicializar o app
app = dash.Dash(__name__)

# Layout do Dashboard
app.layout = html.Div([
    html.H1("Dashboard-SO", style={'text-align': 'center'}),
    
    # Dropdown para seleção de opções
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Opção 1', 'value': 'OP1'},
            {'label': 'Opção 2', 'value': 'OP2'},
            {'label': 'Opção 3', 'value': 'OP3'}
        ],
        value='OP1',
        placeholder="Selecione uma opção",
        style={'width': '50%', 'margin': 'auto'}
    ),

    # Gráfico de exemplo
    dcc.Graph(
        id='graph',
        style={'margin-top': '20px'}
    ),

    # Seção de texto dinâmico
    html.Div(
        id='output-text',
        style={'text-align': 'center', 'margin-top': '20px', 'font-size': '20px'}
    )
])

# Callbacks para interatividade
@app.callback(
    [Output('graph', 'figure'), Output('output-text', 'children')],
    [Input('dropdown', 'value')]
)
def update_dashboard(selected_value):
    # Dados do gráfico
    if selected_value == 'OP1':
        data = {'x': [1, 2, 3], 'y': [10, 20, 30], 'name': 'Série 1'}
    elif selected_value == 'OP2':
        data = {'x': [1, 2, 3], 'y': [30, 10, 20], 'name': 'Série 2'}
    else:
        data = {'x': [1, 2, 3], 'y': [20, 30, 10], 'name': 'Série 3'}

    figure = {
        'data': [
            {'x': data['x'], 'y': data['y'], 'type': 'line', 'name': data['name']}
        ],
        'layout': {
            'title': f'Gráfico para {selected_value}',
            'xaxis': {'title': 'Eixo X'},
            'yaxis': {'title': 'Eixo Y'}
        }
    }

    # Texto dinâmico
    text = f"Você selecionou: {selected_value}"

    return figure, text

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)

