import io
import pandas as pd
import dash
from dash import dcc as dcc
from dash import html as html
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from xlsxwriter import Workbook
import flask


app = dash.Dash(__name__)
server = app.server

# Carregar os dados dos arquivos JSON
df_acesso_certificado = pd.read_json('./dados/acesso_e_certificados.json')
df_qtd_inscritos = pd.read_json('./dados/qtd_inscritos.json')
df_qtd_acessos = pd.read_json('./dados/qtd_acessos.json')


# Filtrar os dados conforme os critérios desejados
filtro_curso = [
    'AcDOC - Capacitação em Pesquisa',
    'AcDOC - Como evitar a dispersão: foco e disciplina',
    'AcDOC - Curadoria',
    'AcDOC - Descomplicando o Instrumento de Avaliação de Cursos',
    'AcDOC - Lifelong Learning',
    'AcDOC - Metaverso',
    'AcDOC - Neurociência da Aprendizagem',
    'AcDOC - Reskilling: Aprendendo A Aprender'
]
df_acesso_certificado_filtrado = df_acesso_certificado[
    df_acesso_certificado['curso'].isin(filtro_curso)
]
df_qtd_inscritos_filtrado = df_qtd_inscritos[
    df_qtd_inscritos['nome_curso'].isin(filtro_curso)
]
df_qtd_acessos_filtrado = df_qtd_acessos[
    df_qtd_acessos['nome_curso'].isin(filtro_curso)
]


# Criar o gráfico de barras interativo para quantidade de inscritos por curso
fig_inscritos = go.Figure(
    data=go.Bar(
        x=df_qtd_inscritos_filtrado['alunos_inscritos'],
        y=df_qtd_inscritos_filtrado['nome_curso'],
        text=df_qtd_inscritos_filtrado['alunos_inscritos'],
        textposition='inside',
        orientation='h',
        marker=dict(color='#1f2c51')
    )
)

fig_inscritos.update_layout(
    title={
        'text': '<b>Quantidade de Inscritos por Curso</b>',
        'x': 0.5,
        'font': {'size': 24}},
    yaxis_title='<b>Cursos</b>',
    barmode='group',
)


# Criar o gráfico de barras interativo para quantidade de acessos por curso
fig_acessos = go.Figure(
    data=go.Bar(
        x=df_qtd_acessos_filtrado['alunos_acessaram'],
        y=df_qtd_acessos_filtrado['nome_curso'],
        text=df_qtd_acessos_filtrado['alunos_acessaram'],
        textposition='inside',
        orientation='h',
        marker=dict(color='#1f2c51')
    )
)
fig_acessos.update_layout(
    title={
        'text': '<b>Quantidade de Acessos por Curso</b>',
        'x': 0.5,
        'font': {'size': 24}},
    yaxis_title='<b>Cursos</b>',
    barmode='group',
)

# Filtrar os alunos que emitiram certificados
df_certificados_emitidos = df_acesso_certificado_filtrado[
    df_acesso_certificado_filtrado['status_certificado'] == 'Emitiu Certificado'
]

# Contar a quantidade de certificados emitidos por curso
df_certificados_por_curso = df_certificados_emitidos['curso'].value_counts(
).reset_index()
df_certificados_por_curso.columns = ['curso', 'certificados_emitidos']


# Criar o gráfico de barras interativo para quantidade de certificados emitidos por curso
fig_certificados = go.Figure(
    data=go.Bar(
        x=df_certificados_por_curso['certificados_emitidos'],
        y=df_certificados_por_curso['curso'],
        text=df_certificados_por_curso['certificados_emitidos'],
        textposition='inside',
        orientation='h',
        marker=dict(color='#1f2c51'),
        hovertemplate='%{text} certificados emitidos'
    )
)


fig_certificados.update_layout(
    title={
        'text': '<b>Quantidade de Certificados Emitidos por Curso</b>',
        'x': 0.5,
        'font': {'size': 24}},
    yaxis_title='<b>Cursos</b>',
    barmode='group'
)

# Criar o layout do dashboard


app.css.append_css({
    "external_url": "https://fonts.googleapis.com/css2?family=Roboto"
})

# Estilizar a página com um background color personalizado
app.layout = html.Div(

    style={'backgroundColor': '#1F2B50'},  # Cor de fundo personalizada
    children=[
        html.H1(
            children='Dashboard Cursos AcDOC',
            style={
                'fontWeight': 'bold',
                'fontSize': '48px',
                'textAlign': 'center',
                'color': 'white',
                'fontFamily': 'Lucida Sans'
            }
        ),

        html.Div(
            className='card',
            style={'backgroundColor': '#42547b',
                   'padding': '20px', 'margin-bottom': '20px', 'fontWeight': 'bold', 'textAlign': 'right'},
            children=[
                html.Button('Exportar', id='export-button-inscritos'),
                dcc.Download(id='download-inscritos'),
                dcc.Graph(id='graph-inscritos', figure=fig_inscritos)
            ]
        ),

        html.Div(
            className='card',
            style={'backgroundColor': '#42547b',
                   'padding': '20px', 'margin-bottom': '20px', 'fontWeight': 'bold', 'textAlign': 'right'},
            children=[
                html.Button('Exportar', id='export-button-acessos'),
                dcc.Download(id='download-acessos'),
                dcc.Graph(id='graph-acessos', figure=fig_acessos)
            ]
        ),

        html.Div(
            className='card',
            style={'backgroundColor': '#42547b',
                   'padding': '20px', 'margin-bottom': '20px', 'fontWeight': 'bold', 'textAlign': 'right'},
            children=[
                html.Button('Exportar', id='export-button-certificados'),
                dcc.Download(id='download-certificados'),
                dcc.Graph(id='graph-certificados', figure=fig_certificados)
            ]
        )
    ]
)


@app.callback(
    Output('download-inscritos', 'data'),
    Input('export-button-inscritos', 'n_clicks')
)
def export_data_inscritos(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    # Passo 1: Obter os dados a serem exportados
    excel_data = io.BytesIO()
    with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
        df_qtd_inscritos_filtrado.to_excel(writer, index=False, header=True)
    excel_data.seek(0)

    # Passo 2: Criar o objeto de dados para download
    return dcc.send_bytes(excel_data.getvalue(), "AcDOC-Inscritos.xlsx")


@app.callback(
    Output('download-acessos', 'data'),
    Input('export-button-acessos', 'n_clicks')
)
def export_data_acessos(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    # Passo 1: Obter os dados a serem exportados
    excel_data = io.BytesIO()
    with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
        df_qtd_acessos_filtrado.to_excel(writer, index=False, header=True)
    excel_data.seek(0)

    # Passo 2: Criar o objeto de dados para download
    return dcc.send_bytes(excel_data.getvalue(), "AcDOC-Acessos.xlsx")


@app.callback(
    Output('download-certificados', 'data'),
    Input('export-button-certificados', 'n_clicks')
)
def export_data_certificados(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    # Passo 1: Obter os dados a serem exportados
    excel_data = io.BytesIO()
    with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
        df_acesso_certificado_filtrado.to_excel(
            writer, index=False, header=True)
    excel_data.seek(0)

    # Passo 2: Criar o objeto de dados para download
    return dcc.send_bytes(excel_data.getvalue(), "AcDOC-Certificados.xlsx")


@server.route('/dashboard')
def dashboard():
    return app.index()


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8080)
