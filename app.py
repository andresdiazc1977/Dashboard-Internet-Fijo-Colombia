# import psutil
# import time
# import threading
# import os

# def monitor_recursos(file_path, interval=1):
#     process = psutil.Process()
#     with open(file_path, 'w') as file:
#         file.write("Fecha, Uso CPU, Uso Memoria (MB), Lectura Disco (MB), Escritura Disco (MB), "
#                    "Datos Enviados (MB), Datos Recibidos (MB), Hilos, Tiempo de CPU (Usuario), Tiempo de CPU (Sistema), Archivos abiertos\n")
#         try:
#             while True:
#                 fecha = time.strftime("%Y-%m-%d %H:%M:%S")
#                 uso_cpu = process.cpu_percent(interval=interval)
#                 uso_memoria = process.memory_info()
#                 uso_memoria = uso_memoria.rss / (1024 * 1024)

#                 io = process.io_counters()
#                 lectura_disco = io.read_bytes / (1024 * 1024)
#                 escritura_disco = io.write_bytes / (1024 * 1024)

#                 io_red = psutil.net_io_counters(pernic=False)
#                 datos_enviados = io_red.bytes_sent / (1024 * 1024)
#                 datos_recibidos = io_red.bytes_recv / (1024 * 1024) 

#                 hilos = process.num_threads()

#                 cpu = process.cpu_times()
#                 cpu_usuario = cpu.user
#                 cpu_sistema = cpu.system

#                 open_files = len(process.open_files())

#                 file.write(f"{fecha}, {uso_cpu}, {uso_memoria}, {lectura_disco}, {escritura_disco}, "
#                            f"{datos_enviados}, {datos_recibidos}, {hilos}, {cpu_usuario}, {cpu_sistema}, {open_files}\n")
#                 file.flush() 
#                 time.sleep(interval)
#         except psutil.NoSuchProcess:
#             print("Process terminated.")
#         except KeyboardInterrupt:
#             print("Monitoring stopped.")

# def iniciar_monitoreo(file_path):
#     monitor_thread = threading.Thread(target=monitor_recursos, args=(file_path,))
#     monitor_thread.daemon = True
#     monitor_thread.start()

# tests_folder = os.path.join(os.path.dirname(__file__), 'tests')
# #tests_path = os.path.join(tests_folder, 'monitoreo_recursos_multicarga.txt')
# tests_path = os.path.join(tests_folder, 'monitoreo_recursos.txt')

# if __name__ == "__main__":
#     iniciar_monitoreo(tests_path)

import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import dash_table
import pandas as pd
import json
import requests
import os

# Cargar plantilla
load_figure_template('MINTY')

# Inicializar la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server

# Configurar el título de la aplicación
app.title = 'Dashboard Internet Fijo'

# Ruta de datos
data_folder = os.path.join(os.path.dirname(__file__), 'data')

# Carga de dataset Accesos
accesos_path = os.path.join(data_folder, 'Accesos.csv')
df_Accesos = pd.read_csv(accesos_path, delimiter=';') 
df_Accesos['VELOCIDAD_EFECTIVA_DOWNSTREAM'] = pd.to_numeric(df_Accesos['VELOCIDAD_EFECTIVA_DOWNSTREAM'], errors='coerce')
df_Accesos['VELOCIDAD_EFECTIVA_UPSTREAM'] = pd.to_numeric(df_Accesos['VELOCIDAD_EFECTIVA_UPSTREAM'], errors='coerce')
df_Accesos = df_Accesos[(df_Accesos['ANNO'] >= 2022)]

# Carga de dataset Ingresos
ingresos_path = os.path.join(data_folder, 'Ingresos.csv')
df_Ingresos = pd.read_csv(ingresos_path, delimiter=';') 
df_Ingresos = df_Ingresos[(df_Ingresos['ANNO'] >= 2022)]

# Carga de dataset Quejas
quejas_path = os.path.join(data_folder, 'Quejas.csv')
df_Quejas = pd.read_csv(quejas_path, delimiter=';') 
df_Quejas = df_Quejas[(df_Quejas['ANNO'] >= 2022)]

# Carga y limpieza de dataset Empaquetamiento
empaquetamiento_path = os.path.join(data_folder, 'Empaquetamiento.csv')
df_Empaquetamiento = pd.read_csv(empaquetamiento_path, delimiter=';', low_memory=False)
df_Empaquetamiento = df_Empaquetamiento[(df_Empaquetamiento['ANNO'] >= 2022)]
df_Empaquetamiento = df_Empaquetamiento.drop(['VELOCIDAD_EFECTIVA_DOWNSTREAM', 'VELOCIDAD_EFECTIVA_UPSTREAM',
                                              'ID_TECNOLOGIA', 'TECNOLOGIA', 'ID_ESTADO', 'ESTADO',
                                              'VALOR_FACTURADO_O_COBRADO', 'OTROS_VALORES_FACTURADOS'], axis=1)
df_Empaquetamiento = df_Empaquetamiento.drop(df_Empaquetamiento[df_Empaquetamiento['SERVICIO_PAQUETE'] == 'Telefonía fija'].index)
df_Empaquetamiento = df_Empaquetamiento.drop(df_Empaquetamiento[df_Empaquetamiento['SERVICIO_PAQUETE'] == 'Televisión por suscripción'].index)
df_Empaquetamiento = df_Empaquetamiento.drop(df_Empaquetamiento[df_Empaquetamiento['SERVICIO_PAQUETE'] == 'Duo Play 3 (Telefonía fija y TV por suscripción)'].index)

# Carga y limpieza de dataset Penetracion
penetracion_path = os.path.join(data_folder, 'Penetracion.csv')
df_Penetracion = pd.read_csv(penetracion_path, delimiter=',')
df_Penetracion = df_Penetracion[(df_Penetracion['a_o'] >= 2022)]
df_Penetracion.rename(columns = {'a_o':'ANNO'}, inplace = True)
df_Penetracion.rename(columns = {'trimestre':'TRIMESTRE'}, inplace = True)
df_Penetracion.rename(columns = {'departamento':'DEPARTAMENTO'}, inplace = True)
df_Penetracion.rename(columns = {'no_accesos_fijos_a_internet':'ACCESOS'}, inplace = True)
df_Penetracion.rename(columns = {'poblaci_n_dane':'POBLACION'}, inplace = True)
df_Penetracion.rename(columns = {'indice':'PENETRACION'}, inplace = True)
df_Penetracion['PENETRACION'] = df_Penetracion['PENETRACION'].str.replace(',', '.')
df_Penetracion['PENETRACION'] = pd.to_numeric(df_Penetracion['PENETRACION'], errors='coerce')
df_Penetracion['cod_departamento'] = df_Penetracion['cod_departamento'].astype(str)
df_Penetracion['cod_departamento'] = df_Penetracion['cod_departamento'].str.zfill(2)
df_Penetracion_Faltante = df_Penetracion[(df_Penetracion['ANNO'] == 2023) & (df_Penetracion['TRIMESTRE'] == 3)]
df_Penetracion_Faltante.loc[:, 'TRIMESTRE'] = 4
df_Penetracion = pd.concat([df_Penetracion, df_Penetracion_Faltante])

#Carga Mapa de Colombia por Departamentos
mapa_path = os.path.join(data_folder, 'Departamentos.json')
with open(mapa_path, 'r', encoding='utf-8') as f:
    mapadepartamentos = json.load(f)

# Obtener el mayor año y trimestre dentro de ese año para establecerlo por defecto en los filtros
ultimo_anno = df_Accesos['ANNO'].max()
ultimo_trimestre = df_Accesos[df_Accesos['ANNO'] == ultimo_anno]['TRIMESTRE'].max()

# Layout de la aplicación
app.layout = html.Div([
    # Encabezado
    html.Div([
        dbc.Col(html.H5('Indicadores Trimestrales de Internet Fijo en Colombia desde 2022',className='bg-primary text-white p-2 mb-3'),)
    ], style={'textAlign': 'center', 'backgroundColor': '#f8f9fa'}),
    # Barra lateral con filtros
    html.Div([
        dbc.Row(html.H6('Filtros', className='bg-dark text-white p-2 mb-3'),),
        dbc.Row([
            dbc.Col([
                html.Label("Seleccione el año"),
                dcc.Dropdown(id='anno-filtro',
                            options=[{'label': anno, 'value': anno} for anno in df_Accesos['ANNO'].unique()],
                            value=ultimo_anno,
                            style={'width': '100%'}
                ),
            ],lg=3),
            dbc.Col([   
                html.Label("Seleccione el trimestre"),
                dcc.Dropdown(id='trimestre-filtro',
                            options=[{'label': trimestre, 'value': trimestre} for trimestre in df_Accesos['TRIMESTRE'].unique()],
                            value=ultimo_trimestre,
                            style={'width': '100%'}
                ),
            ],lg=3),
            dbc.Col([
                html.Label("Seleccione uno o varios Departamentos"),
                dcc.Dropdown(id='departamento-filtro',
                            options=[{'label': departamento, 'value': departamento} for departamento in sorted(df_Accesos['DEPARTAMENTO'].unique())],
                            style={'width': '100%', 'overflow-wrap': 'break-word', 'white-space': 'normal'},
                            multi=True
                ),
            ],lg=3),
            dbc.Col([ 
                html.Label("Seleccione uno o varios Municipios"),
                dcc.Dropdown(id='municipio-filtro',
                            style={'width': '100%', 'overflow-wrap': 'break-word', 'white-space': 'normal'},
                            multi=True
                ),
            ],lg=3),
        ]),
        dbc.Row([
            html.P([html.Br()], style={'font-size': '5px'}),
            html.Div(["Los filtros", html.B(" Año "), "y", html.B(" Trimestre "), "aplican para todos los indicadores. ",
                      "Los filtros", html.B(" Departamento "), "y", html.B(" Municipio "), "aplican únicamente para las Pestañas Mercado, Velocidad de Descarga y Tecnología de Conexión."],
                      className="card text-white bg-danger mb-3",style={'overflow-wrap': 'break-word', 'white-space': 'normal', 'width': '100%', 'display': 'block'}),
        ]),
    ], style={'width': '100%','display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px', 'marginLeft': '10px'}),
    # Panel principal
    html.Div([
        # Cuatro indicadores que siempre están presentes
        html.Div([
            dbc.Row(html.H6(id='encabezado', className='bg-info text-white p-2 mb-3'),),
            dbc.Row([
                dbc.Col(dcc.Graph(id='total-accesos-gauge', config={'responsive': True}), lg=3),
                dbc.Col(dcc.Graph(id='velocidad-promedio-gauge', config={'responsive': True}), lg=3),
                dbc.Col(dcc.Graph(id='ingresos-gauge', config={'responsive': True}), lg=3),
                dbc.Col(dcc.Graph(id='quejas_gauge', config={'responsive': True}), lg=3),
            ]),
        ]),
        # Pestañas con gráficos adicionales
        dbc.Row(html.H6(id='titulo', className='bg-info text-white p-2 mb-3')),
        dcc.Tabs(id='tabs', value='tab-6', children=[
            dcc.Tab(label='Portada', value='tab-6', style={'padding': '5px'}, className='bg-info text-white p-2 mb-3'),
            dcc.Tab(label='Mercado', value='tab-1', style={'padding': '5px'}, className='bg-info text-white p-2 mb-3'),
            dcc.Tab(label='Ingresos', value='tab-2', style={'padding': '5px'}, className='bg-info text-white p-2 mb-3'),
            dcc.Tab(label='Velocidad de Descarga', style={'padding': '5px'}, value='tab-3', className='bg-info text-white p-2 mb-3'),
            dcc.Tab(label='Tecnología de Conexión', style={'padding': '5px'}, value='tab-4', className='bg-info text-white p-2 mb-3'),
            dcc.Tab(label='Quejas', value='tab-5', style={'padding': '5px'}, className='bg-info text-white p-2 mb-3'),
            dcc.Tab(label='Acerca de', value='tab-7', style={'padding': '5px'}, className='bg-info text-white p-2 mb-3'),
        ]),
        html.Div(id='tabs-content')
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '10px', 'marginLeft': '10px'})
], style={'width': '100%', 'display': 'flex', 'flexDirection': 'column', 'verticalAlign': 'top', 'overflowY': 'auto', 'overflowX': 'auto', 'maxHeight': '100vh'})

# Callback para mostrar el año y el trimestre seleccionados en el encabezado
@app.callback(
    Output('encabezado', 'children'),
    [Input('anno-filtro', 'value'),
     Input('trimestre-filtro', 'value')]
)
def actualizar_encabezado(anno, trimestre):
    return f"Indicadores clave a nivel nacional para el año {anno} trimestre {trimestre}"

# Callback para actualizar los municipios basados en los departamentos seleccionados
@app.callback(
    Output('municipio-filtro', 'options'),
    [Input('departamento-filtro', 'value')]
)
def set_municipio_options(selected_departamentos):
    if not selected_departamentos:
        return []
    df_Municipios = df_Accesos[df_Accesos['DEPARTAMENTO'].isin(selected_departamentos)]
    selected_municipios = [{'label': municipio, 'value': municipio} for municipio in sorted(df_Municipios['MUNICIPIO'].unique())]
    return selected_municipios

# Callback para mostrar los departamentos y municipios seleccionados en el titulo
@app.callback(
    Output('titulo', 'children'),
    [Input('departamento-filtro', 'value'),
     Input('municipio-filtro', 'value'),
     Input('tabs', 'value')]
)

def actualizar_titulo(departamento, municipio, tab):
    if departamento or municipio:
        filtros_seleccionados = []
        if departamento:
            if isinstance(departamento, list):
                filtros_seleccionados.extend(departamento)
            else:
                filtros_seleccionados.append(departamento)
        if municipio:
            if isinstance(municipio, list):
                filtros_seleccionados.extend(municipio)
            else:
                filtros_seleccionados.append(municipio)

        if tab == 'tab-1':
            return f'Mercado para {", ".join(filtros_seleccionados)}' if filtros_seleccionados else 'Mercado a nivel nacional'
        elif tab == 'tab-2':
            return 'Los Ingresos solamente se pueden visualizar a nivel nacional'
        elif tab == 'tab-3':
            return f'Velocidad de Descarga para {", ".join(filtros_seleccionados)}' if filtros_seleccionados else 'Velocidad de Descarga a nivel nacional'
        elif tab == 'tab-4':
            return f'Tecnología de Conexión para {", ".join(filtros_seleccionados)}' if filtros_seleccionados else 'Tecnología de Conexión a nivel nacional'
        elif tab == 'tab-5':
            return 'Las Quejas solamente se pueden visualizar a nivel nacional'
        elif tab == 'tab-6':
            return 'Portada: Penetración a nivel nacional'
        elif tab == 'tab-7':
            return 'Acerca de'
        else:
            return ''
    else:
        if tab == 'tab-1':
            return 'Mercado a nivel nacional'
        elif tab == 'tab-2':
            return 'Ingresos a nivel nacional'
        elif tab == 'tab-3':
            return 'Velocidad de Descarga a nivel nacional'
        elif tab == 'tab-4':
            return 'Tecnología de Conexión a nivel nacional'
        elif tab == 'tab-5':
            return 'Quejas a nivel nacional'
        elif tab == 'tab-6':
            return 'Portada: Penetración a nivel nacional'
        elif tab == 'tab-7':
            return 'Acerca de'
        else:
            return ''

# Funciones para filtrar los datasets según los filtros de año y trimestre seleccionados
def filtro_datos_accesos(anno, trimestre):
    df_Accesos_filtrado = df_Accesos.copy()
    if anno:
        df_Accesos_filtrado = df_Accesos_filtrado[df_Accesos_filtrado['ANNO'] == anno]
    if trimestre:
        df_Accesos_filtrado = df_Accesos_filtrado[df_Accesos_filtrado['TRIMESTRE'] == trimestre]
    return df_Accesos_filtrado

def filtro_datos_ingresos(anno, trimestre):
    df_Ingresos_filtrado = df_Ingresos.copy()
    if anno:
        df_Ingresos_filtrado = df_Ingresos_filtrado[df_Ingresos_filtrado['ANNO'] == anno]
    if trimestre:
        df_Ingresos_filtrado = df_Ingresos_filtrado[df_Ingresos_filtrado['TRIMESTRE'] == trimestre]
    return df_Ingresos_filtrado

def filtro_datos_quejas(anno, trimestre):
    df_Quejas_filtrado = df_Quejas.copy()
    if anno:
        df_Quejas_filtrado = df_Quejas_filtrado[df_Quejas_filtrado['ANNO'] == anno]
    if trimestre:
        df_Quejas_filtrado = df_Quejas_filtrado[df_Quejas_filtrado['TRIMESTRE'] == trimestre]
    return df_Quejas_filtrado

def filtro_datos_empaquetamiento(anno, trimestre):
    df_Empaquetamiento_filtrado = df_Empaquetamiento.copy()
    if anno:
        df_Empaquetamiento_filtrado = df_Empaquetamiento_filtrado[df_Empaquetamiento_filtrado['ANNO'] == anno]
    if trimestre:
        df_Empaquetamiento_filtrado = df_Empaquetamiento_filtrado[df_Empaquetamiento_filtrado['TRIMESTRE'] == trimestre]
    return df_Empaquetamiento_filtrado

def filtro_datos_penetracion(anno, trimestre):
    df_Penetracion_filtrado = df_Penetracion.copy()
    if anno:
        df_Penetracion_filtrado = df_Penetracion_filtrado[df_Penetracion_filtrado['ANNO'] == anno]
    if trimestre:
        df_Penetracion_filtrado = df_Penetracion_filtrado[df_Penetracion_filtrado['TRIMESTRE'] == trimestre]
    return df_Penetracion_filtrado

# Función para actualizar los indicadores fijos
@app.callback(
    [Output('total-accesos-gauge', 'figure'),
     Output('velocidad-promedio-gauge', 'figure'),
     Output('ingresos-gauge', 'figure'),
     Output('quejas_gauge', 'figure')],
    [Input('anno-filtro', 'value'),
     Input('trimestre-filtro', 'value')]
)

def actualizar_graficas_fijas(anno, trimestre):
    # Preparacion de los datos
    df_Accesos_filtrado = filtro_datos_accesos(anno, trimestre)
    total_accesos = df_Accesos_filtrado['ACCESOS'].sum()
    velocidad = (df_Accesos_filtrado['VELOCIDAD_EFECTIVA_DOWNSTREAM']*df_Accesos_filtrado['ACCESOS']).sum()
    promedio_velocidad = velocidad/total_accesos
    df_Ingresos_filtrado = filtro_datos_ingresos(anno, trimestre)
    total_ingresos = df_Ingresos_filtrado['INGRESOS'].sum()
    total_ingresos = total_ingresos/1000000000000
    df_Quejas_filtrado = filtro_datos_quejas(anno, trimestre)
    total_quejas = df_Quejas_filtrado['NUMERO_QUEJAS'].sum()
    # Gráfico de medidor con el total de accesos
    total_accesos_gauge = go.Figure(go.Indicator(
        mode = 'gauge+number',
        value = total_accesos,
        title = {'text': 'Total Accesos'},
        gauge = {'axis': {'range': [None, 10000000]},
                    'steps' : [
                        {'range': [0, 2000000], 'color': 'gainsboro'},
                        {'range': [2000000, 4000000], 'color': 'lightgrey'},
                        {'range': [4000000, 6000000], 'color': 'lightgray'},
                        {'range': [6000000, 8000000], 'color': 'silver'}],
                    'threshold' : {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': 9990000}}
    ))
    total_accesos_gauge.update_layout(autosize=True)
    # Gráfico de medidor con el promedio de velocidad de descarga
    velocidad_promedio_gauge = go.Figure(go.Indicator(
        mode = 'gauge+number',
        value = promedio_velocidad,
        title = {'text': 'Velocidad Promedio Descarga (Mbps)'},
        gauge = {'axis': {'range': [None, 1000]},
                 'steps' : [
                     {'range': [0, 200], 'color': 'gainsboro'},
                     {'range': [200, 400], 'color': 'lightgrey'},
                     {'range': [400, 600], 'color': 'lightgray'},
                     {'range': [600, 800], 'color': 'silver'}],
                 'threshold' : {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': 990}}
    ))
    velocidad_promedio_gauge.update_layout(autosize=True)
    # Gráfico de medidor con el total de ingresos
    ingresos_gauge = go.Figure(go.Indicator(
        mode = 'gauge+number',
        value = total_ingresos,
        title = {'text': 'Total Ingresos (Billones Pesos)'},
        gauge = {'axis': {'range': [None, 2.5]},
                'steps' : [
                    {'range': [0, 0.5], 'color': 'gainsboro'},
                    {'range': [0.5, 1], 'color': 'lightgrey'},
                    {'range': [1, 1.5], 'color': 'lightgray'},
                    {'range': [1.5, 2], 'color': 'silver'}],
                'threshold' : {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': 2.49}}
    ))
    velocidad_promedio_gauge.update_layout(autosize=True)
    # Gráfico de medidor con el total de quejas
    quejas_gauge = go.Figure(go.Indicator(
        mode = 'gauge+number',
        value = total_quejas,
        title = {'text': 'Total Quejas'},
        gauge = {'axis': {'range': [None, 1000000]},
                     'steps' : [
                     {'range': [0, 200000], 'color': 'gainsboro'},
                     {'range': [200000, 400000], 'color': 'lightgrey'},
                     {'range': [400000, 600000], 'color': 'lightgray'},
                     {'range': [600000, 800000], 'color': 'silver'}],
                 'threshold' : {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': 990000}}
    ))
    quejas_gauge.update_layout(autosize=True)

    return [total_accesos_gauge, velocidad_promedio_gauge, ingresos_gauge, quejas_gauge]

# Función para actualizar el contenido de las pestañas
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('anno-filtro', 'value'),
     Input('trimestre-filtro', 'value'),
     Input('departamento-filtro', 'value'),
     Input('municipio-filtro', 'value')]
)

def actualizar_graficas_tabs (tab, anno, trimestre, selected_departamentos, selected_municipios):
# Preparacion de los datos
    # Dataset Accesos
    df_Accesos_filtrado_geografia = filtro_datos_accesos_geografia(anno, trimestre, selected_departamentos, selected_municipios)
    df_Accesos_filtrado2 = df_Accesos_filtrado_geografia.copy()
    total_accesos = df_Accesos_filtrado_geografia['ACCESOS'].sum()
    top_10_empresas = df_Accesos_filtrado2.groupby('EMPRESA')['ACCESOS'].sum().sort_values(ascending=False).reset_index()
    top_10_empresas = top_10_empresas.sort_values('ACCESOS', ascending=False).head(10)
    top_10_nombres = top_10_empresas['EMPRESA'].tolist()
    df_Accesos_filtrado2['EMPRESA_TOP10'] = df_Accesos_filtrado2['EMPRESA'].apply(lambda x: x if x in top_10_nombres else 'OTROS')
    top_10_empresas = df_Accesos_filtrado2.groupby('EMPRESA_TOP10')['ACCESOS'].sum().sort_values(ascending=True).reset_index()
    top_10_empresas.rename(columns = {'EMPRESA_TOP10':'EMPRESA'}, inplace = True)
    top_10_empresas['Porcentaje'] = top_10_empresas['ACCESOS'] / total_accesos * 100
    df_Accesos_filtrado3 = df_Accesos_filtrado_geografia.copy()
    top_10_tecnologias = df_Accesos_filtrado3.groupby('TECNOLOGIA')['ACCESOS'].sum().sort_values(ascending=False).reset_index()
    top_10_tecnologias = top_10_tecnologias.sort_values('ACCESOS', ascending=False).head(10)
    top_10_nombres_tec = top_10_tecnologias['TECNOLOGIA'].tolist()
    df_Accesos_filtrado3['TECNOLOGIA_TOP10'] = df_Accesos_filtrado3['TECNOLOGIA'].apply(lambda x: x if x in top_10_nombres_tec else 'Otras')
    top_10_tecnologias = df_Accesos_filtrado3.groupby('TECNOLOGIA_TOP10')['ACCESOS'].sum().sort_values(ascending=False).reset_index()
    top_10_tecnologias.rename(columns = {'TECNOLOGIA_TOP10':'TECNOLOGIA'}, inplace = True)
    top_10_tecnologias['Porcentaje'] = top_10_tecnologias['ACCESOS'] / total_accesos * 100
    df_Accesos_filtrado4 = df_Accesos_filtrado_geografia.copy()
    etiquetas_velocidad = ['0-10', '10-50', '50-100', '100-500', '500-1000', '>1000']
    bordes_velocidad = [0, 10, 50, 100, 500, 1000, 5000]
    df_Accesos_filtrado4['VELOCIDAD'] = pd.cut(df_Accesos_filtrado4['VELOCIDAD_EFECTIVA_DOWNSTREAM'], bins=bordes_velocidad, labels=etiquetas_velocidad)
    velocidades = df_Accesos_filtrado4.groupby('VELOCIDAD')['ACCESOS'].sum().reset_index()
    segmentos = df_Accesos_filtrado_geografia.groupby(['SEGMENTO'])['ACCESOS'].sum().reset_index()
    df_Accesos_filtrado5 = df_Accesos_filtrado_geografia.copy()
    df_Accesos_filtrado5['VELOCIDAD'] = pd.cut(df_Accesos_filtrado5['VELOCIDAD_EFECTIVA_DOWNSTREAM'], bins=bordes_velocidad, labels=etiquetas_velocidad)
    velocidades_segmento = df_Accesos_filtrado5.groupby(['SEGMENTO','VELOCIDAD'])['ACCESOS'].sum().reset_index()
    # Dataset Ingresos   
    df_Ingresos_filtrado = filtro_datos_ingresos(anno, trimestre)
    total_ingresos = df_Ingresos_filtrado['INGRESOS'].sum()
    total_ingresos = total_ingresos/1000000000000
    df_Ingresos_filtrado2 = df_Ingresos_filtrado.copy()
    top_10_empresas_ingresos = df_Ingresos_filtrado2.groupby('EMPRESA')['INGRESOS'].sum().sort_values(ascending=False).reset_index()
    top_10_empresas_ingresos = top_10_empresas_ingresos.sort_values('INGRESOS', ascending=False).head(10)
    top_10_nombres_ingresos = top_10_empresas_ingresos['EMPRESA'].tolist()
    df_Ingresos_filtrado2['EMPRESA_TOP10'] = df_Ingresos_filtrado2['EMPRESA'].apply(lambda x: x if x in top_10_nombres_ingresos else 'OTROS')
    top_10_empresas_ingresos = df_Ingresos_filtrado2.groupby('EMPRESA_TOP10')['INGRESOS'].sum().sort_values(ascending=True).reset_index()
    top_10_empresas_ingresos.rename(columns = {'EMPRESA_TOP10':'EMPRESA'}, inplace = True)
    top_10_empresas_ingresos['INGRESOS'] = top_10_empresas_ingresos['INGRESOS']/1000000000
    total_ingresos2 = df_Ingresos_filtrado['INGRESOS'].sum()
    total_ingresos2 = total_ingresos2/1000000000
    top_10_empresas_ingresos['Porcentaje'] = top_10_empresas_ingresos['INGRESOS'] / total_ingresos2 * 100
    # Merge Ingresos y Accesos para calcular ARPU
    df_Accesos_filtrado_arpu = filtro_datos_accesos(anno, trimestre)
    top_10_empresas_arpu = df_Accesos_filtrado_arpu.groupby('EMPRESA')['ACCESOS'].sum().sort_values(ascending=False).reset_index()
    top_10_empresas_arpu = top_10_empresas_arpu.sort_values('ACCESOS', ascending=False).head(10)
    top_10_empresas_arpu = top_10_empresas_arpu['EMPRESA'].tolist()
    AccesosEmpresa = df_Accesos_filtrado_arpu.groupby(['ID_EMPRESA','EMPRESA'])['ACCESOS'].sum().sort_values(ascending=False).reset_index()
    IngresosEmpresas = df_Ingresos_filtrado.groupby(['ID_EMPRESA','EMPRESA'])['INGRESOS'].sum().sort_values(ascending=False).reset_index()
    arpu = pd.merge(AccesosEmpresa, IngresosEmpresas, on='ID_EMPRESA', how='inner')
    arpu.rename(columns={'EMPRESA_x': 'EMPRESA'}, inplace=True)
    arpu.drop(columns=['EMPRESA_y'], inplace=True)
    arpu['ARPU'] = arpu['INGRESOS'] / arpu['ACCESOS']
    arpu_top10_accesos = arpu[arpu['EMPRESA'].isin(top_10_empresas_arpu)]
    arpu_top10_accesos = arpu_top10_accesos.sort_values(by='ARPU', ascending=True)
    arpu_top10_ingresos = arpu[arpu['EMPRESA'].isin(top_10_nombres_ingresos)]
    arpu_top10_ingresos = arpu_top10_ingresos.sort_values(by='ARPU', ascending=True)
    # Dataset Quejas
    df_Quejas_filtrado = filtro_datos_quejas(anno, trimestre)
    total_quejas = df_Quejas_filtrado['NUMERO_QUEJAS'].sum()
    df_Quejas_filtrado2 = df_Quejas_filtrado.copy()
    top_10_empresas_quejas = df_Quejas_filtrado2.groupby('EMPRESA')['NUMERO_QUEJAS'].sum().sort_values(ascending=False).reset_index()
    top_10_empresas_quejas = top_10_empresas_quejas.sort_values('NUMERO_QUEJAS', ascending=False).head(10)
    top_10_nombres_quejas = top_10_empresas_quejas['EMPRESA'].tolist()
    df_Quejas_filtrado2['EMPRESA_TOP10'] = df_Quejas_filtrado2['EMPRESA'].apply(lambda x: x if x in top_10_nombres_quejas else 'OTROS')
    top_10_empresas_quejas = df_Quejas_filtrado2.groupby('EMPRESA_TOP10')['NUMERO_QUEJAS'].sum().sort_values(ascending=True).reset_index()
    top_10_empresas_quejas.rename(columns = {'EMPRESA_TOP10':'EMPRESA'}, inplace = True)
    top_10_empresas_quejas['Porcentaje'] = top_10_empresas_quejas['NUMERO_QUEJAS'] / total_quejas * 100
    df_Quejas_filtrado2 = df_Quejas_filtrado.copy()
    top_10_tipologia_quejas = df_Quejas_filtrado2.groupby(['TIPOLOGIA'])['NUMERO_QUEJAS'].sum().sort_values(ascending=False).reset_index()
    top_10_tipologia_quejas = top_10_tipologia_quejas.sort_values('NUMERO_QUEJAS', ascending=False).head(10)
    top_10_nombres_tipologia = top_10_tipologia_quejas['TIPOLOGIA'].tolist()
    df_Quejas_filtrado2['TIPOLOGIA_TOP10'] = df_Quejas_filtrado2['TIPOLOGIA'].apply(lambda x: x if x in top_10_nombres_tipologia else 'Otros')
    top_10_tipologia_quejas = df_Quejas_filtrado2.groupby('TIPOLOGIA_TOP10')['NUMERO_QUEJAS'].sum().sort_values(ascending=True).reset_index()
    top_10_tipologia_quejas.rename(columns = {'TIPOLOGIA_TOP10':'TIPOLOGIA'}, inplace = True)
    top_10_tipologia_quejas['Porcentaje'] = top_10_tipologia_quejas['NUMERO_QUEJAS'] / total_quejas * 100
    df_Quejas_filtrado3 = df_Quejas_filtrado.copy()
    medio_quejas = df_Quejas_filtrado3.groupby(['MEDIO_ATENCION'])['NUMERO_QUEJAS'].sum().sort_values(ascending=False).reset_index()
    medio_quejas['Porcentaje'] = medio_quejas['NUMERO_QUEJAS'] / total_quejas * 100
    # Dataset Empaquetamiento
    df_Empaquetamiento_filtrado_geografia = filtro_datos_empaquetamiento_geografia(anno, trimestre, selected_departamentos, selected_municipios)
    empaquetamiento_servicios = df_Empaquetamiento_filtrado_geografia.groupby(['SERVICIO_PAQUETE'])['CANTIDAD_LINEAS_ACCESOS'].sum().sort_values(ascending=False).reset_index()
    total_empaquetado = empaquetamiento_servicios['CANTIDAD_LINEAS_ACCESOS'].sum()
    empaquetamiento_servicios['Porcentaje'] = empaquetamiento_servicios['CANTIDAD_LINEAS_ACCESOS'] / total_empaquetado * 100
    # Dataset Penetración
    df_Penetracion_filtrado = filtro_datos_penetracion(anno, trimestre)
    #df_Penetracion_filtrado_tabla = df_Penetracion_filtrado[['DEPARTAMENTO', 'POBLACION', 'ACCESOS', 'PENETRACION']].sort_values('PENETRACION', ascending=False) 

# Función para seleccionar las pestañas y construir las gráficas
    if tab == 'tab-6':
        color_scale = px.colors.diverging.Temps[::-1]
        MapaPenetracion=px.choropleth(df_Penetracion_filtrado, geojson=mapadepartamentos,locations='cod_departamento', featureidkey='properties.DPTO_CCDGO', color='PENETRACION',
                                      color_continuous_scale=color_scale, hover_name='cod_departamento', hover_data={'DEPARTAMENTO': True,'POBLACION': True,'ACCESOS': True},
                                      labels={'DEPARTAMENTO':'DEPARTAMENTO', 'POBLACION':'POBLACION', 'ACCESOS':'ACCESOS', 'PENETRACION':'PENETRACION'})
        MapaPenetracion.update_geos(fitbounds='locations', visible=False)
        MapaPenetracion.update_layout(margin={'r':0,'t':0,'l':0,'b':0}, dragmode=False)
        MapaPenetracion.update_layout(title='Penetración por Departamento')
        MapaPenetracion.update_layout(autosize=True, width=None, height=None)
        return html.Div([
                        dcc.Graph(id='tab6-graph1', figure=MapaPenetracion, style={'height': '90vh'})
        ])
    elif tab == 'tab-1':
        BarrasAccesos=px.bar(top_10_empresas, y='EMPRESA', x='ACCESOS', orientation='h', title='Accesos por Empresa (Top 10)')        
        BarrasAccesos.update_layout(annotations=[dict(x=0, y=-1, text=f'Total de Accesos: {total_accesos}', showarrow=False)])
        BarrasAccesos.update_layout(autosize=True, width=None, height=None)
        PieAccesos=px.pie(top_10_empresas, values='Porcentaje', names='EMPRESA', title='Participación de Mercado (Top 10)')
        PieAccesos.update_layout(autosize=True, width=None, height=None)
        BarrasEstratoSegmento=px.bar(segmentos, x='SEGMENTO', y='ACCESOS', title='Distribución de Accesos por Estrato y Segmento')
        BarrasEstratoSegmento.update_layout(autosize=True, width=None, height=None)
        PieEmpaquetamiento=px.pie(empaquetamiento_servicios, values='Porcentaje', names='SERVICIO_PAQUETE', title='Empaquetamiento de Servicios')
        PieEmpaquetamiento.update_layout(autosize=True, width=None, height=None)
        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(id='tab1-graph1', figure=BarrasAccesos), lg=6),
                dbc.Col(dcc.Graph(id='tab1-graph2', figure=PieAccesos), lg=6),
                ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='tab1-graph3', figure=BarrasEstratoSegmento), lg=6),
                dbc.Col(dcc.Graph(id='tab1-graph4', figure=PieEmpaquetamiento), lg=6),
                ])
        ])
    elif tab == 'tab-2':
        BarrasIngresos=px.bar(top_10_empresas_ingresos, y='EMPRESA', x='INGRESOS', orientation='h', title='Ingresos por Empresa en Miles de Millones de Pesos (Top 10)')
        BarrasIngresos.update_layout(autosize=True, width=None, height=None)
        PieIngresos=px.pie(top_10_empresas_ingresos, values='Porcentaje', names='EMPRESA', title='Ingresos por Empresa (Top 10)')
        PieIngresos.update_layout(autosize=True, width=None, height=None)
        BarrasArpuAccesos=px.bar(arpu_top10_accesos, y='EMPRESA', x='ARPU', orientation='h', title='Ingreso por Acceso (ARPU) Top 10 Empresas por Accesos')
        BarrasArpuAccesos.update_layout(autosize=True, width=None, height=None)
        BarrasArpuIngresos=px.bar(arpu_top10_ingresos, y='EMPRESA', x='ARPU', orientation='h', title='Ingreso por Acceso (ARPU) Top 10 Empresas por Ingresos')
        BarrasArpuIngresos.update_layout(autosize=True, width=None, height=None)
        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(id='tab2-graph1', figure=BarrasIngresos), lg=6),
                dbc.Col(dcc.Graph(id='tab2-graph2', figure=PieIngresos), lg=6),
                ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='tab2-graph3', figure=BarrasArpuAccesos), lg=6),
                dbc.Col(dcc.Graph(id='tab2-graph4', figure=BarrasArpuIngresos), lg=6),
                ])
        ])
    elif tab == 'tab-3':
        BarrasVelocidades=px.bar(velocidades, x='VELOCIDAD', y='ACCESOS', title='Velocidades de Descarga en Mbps')
        BarrasVelocidades.update_layout(autosize=True, width=None, height=None)
        BarrasVelocidadesSegmentos=px.bar(velocidades_segmento, x='SEGMENTO', y='ACCESOS', color='VELOCIDAD', barmode='group', title='Distribución de Velocidades de Descarga en Mbps por Estrato y Segmento')
        BarrasVelocidadesSegmentos.update_layout(autosize=True, width=None, height=None)
        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(id='tab3-graph1', figure=BarrasVelocidades), lg=6),
                dbc.Col(dcc.Graph(id='tab3-graph2', figure=BarrasVelocidadesSegmentos), lg=6),
                ]),
        ])
    elif tab == 'tab-4':
        TreeTecnologia=px.treemap(top_10_tecnologias, path=['TECNOLOGIA'], values='ACCESOS', title='Accesos por Tecnología')
        TreeTecnologia.update_layout(autosize=True, width=None, height=None)
        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(id='tab4-graph1', figure=TreeTecnologia), lg=12),
                ]),            
        ])
    elif tab == 'tab-5':
        BarrasQuejas=px.bar(top_10_empresas_quejas, y='EMPRESA', x='NUMERO_QUEJAS', orientation='h', title='Quejas por Empresa (Top 10)')
        BarrasQuejas.update_layout(autosize=True, width=None, height=None)
        PieQuejas=px.pie(top_10_empresas_quejas, values='Porcentaje', names='EMPRESA', title='Participación por Empresa (Top 10) en el total de Quejas')
        PieQuejas.update_layout(autosize=True, width=None, height=None)
        TreeTipologiaQuejas=px.treemap(top_10_tipologia_quejas, path=['TIPOLOGIA'], values='NUMERO_QUEJAS', title='Quejas por Tipología')
        TreeTipologiaQuejas.update_layout(autosize=True, width=None, height=None)
        PpieMedioQuejas=px.pie(medio_quejas, values='Porcentaje', names='MEDIO_ATENCION', title='Medio de Atención Quejas')
        PpieMedioQuejas.update_layout(autosize=True, width=None, height=None)
        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(id='tab5-graph1', figure=BarrasQuejas), lg=6),
                dbc.Col(dcc.Graph(id='tab5-graph2', figure=PieQuejas), lg=6),
                ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='tab5-graph3', figure=TreeTipologiaQuejas), lg=6),
                dbc.Col(dcc.Graph(id='tab5-graph4', figure=PpieMedioQuejas), lg=6),
                ])            
        ])
    elif tab == 'tab-7':
        return html.Div([
            dbc.Row([
                html.P([html.Br(),"Esta herramienta de análisis y visualización se desarrolló como proyecto académico dentro del Máster Universitario en Análisis y Visualización de Datos Masivos de la Universidad Internacional de La Rioja.", html.Br()], style={'font-size': '40px'}),
                html.P(["El código fuente se puede consultar en ", html.A("GitHub", href="https://github.com/andresdiazc1977/Dashboard-Internet-Fijo-Colombia/blob/main/", target="_blank"), ".", html.Br()] , style={'font-size': '40px'}),
                html.P(["Los conjuntos de datos abiertos utilizados fueron obtenidos de los portales www.datos.gov.co y www.postdata.gov.co:"], style={'font-size': '40px'}),
                html.A("Accesos de Internet Fijo", href="https://postdata.gov.co/sites/default/files/datasets/data/ACCESOS_INTERNET_FIJO_2_20.csv", target="_blank", style={'font-size': '40px'}),
                html.A("Ingresos de Internet Fijo", href="https://postdata.gov.co/sites/default/files/datasets/data/INGRESOS_INTERNET_FIJO_17.csv", target="_blank", style={'font-size': '40px'}),
                html.A("Quejas de Internet Fijo", href="https://postdata.gov.co/sites/default/files/datasets/data/FT4_2_INT_FIJO_9.csv", target="_blank", style={'font-size': '40px'}),
                html.A("Empaquetamiento de servicios fijos", href="https://postdata.gov.co/sites/default/files/datasets/data/EMPAQUETAMIENTO_FIJO_2.csv", target="_blank", style={'font-size': '40px'}),
                html.A("Internet Fijo Penetración Departamentos", href="https://www.datos.gov.co/resource/4py7-br84.csv?$query=SELECT%0A%20%20%60a_o%60%2C%0A%20%20%60trimestre%60%2C%0A%20%20%60cod_departamento%60%2C%0A%20%20%60departamento%60%2C%0A%20%20%60no_accesos_fijos_a_Internet%60%2C%0A%20%20%60poblaci_n_dane%60%2C%0A%20%20%60indice%60%0A", target="_blank", style={'font-size': '40px'}),
                html.P([html.Br(),html.Br(),html.Br()], style={'font-size': '40px'}),
                ]),
        ])

def filtro_datos_accesos_geografia(anno, trimestre, selected_departamentos, selected_municipios):
    df_Accesos_filtrado_geografia = df_Accesos.copy()
    if anno:
        df_Accesos_filtrado_geografia = df_Accesos_filtrado_geografia[df_Accesos_filtrado_geografia['ANNO'] == anno]
    if trimestre:
        df_Accesos_filtrado_geografia = df_Accesos_filtrado_geografia[df_Accesos_filtrado_geografia['TRIMESTRE'] == trimestre]
    if selected_departamentos:
        df_Accesos_filtrado_geografia = df_Accesos_filtrado_geografia[df_Accesos_filtrado_geografia['DEPARTAMENTO'].isin(selected_departamentos)]
    else:
        df_Accesos_filtrado_geografia = df_Accesos_filtrado_geografia
    if selected_municipios:
        df_Accesos_filtrado_geografia = df_Accesos_filtrado_geografia[df_Accesos_filtrado_geografia['MUNICIPIO'].isin(selected_municipios)]
    return df_Accesos_filtrado_geografia

def filtro_datos_empaquetamiento_geografia(anno, trimestre, selected_departamentos, selected_municipios):
    df_Empaquetamiento_filtrado_geografia = df_Empaquetamiento.copy()
    if anno:
        df_Empaquetamiento_filtrado_geografia = df_Empaquetamiento_filtrado_geografia[df_Empaquetamiento_filtrado_geografia['ANNO'] == anno]
    if trimestre:
        df_Empaquetamiento_filtrado_geografia = df_Empaquetamiento_filtrado_geografia[df_Empaquetamiento_filtrado_geografia['TRIMESTRE'] == trimestre]
    if selected_departamentos:
        df_Empaquetamiento_filtrado_geografia = df_Empaquetamiento_filtrado_geografia[df_Empaquetamiento_filtrado_geografia['DEPARTAMENTO'].isin(selected_departamentos)]
    else:
        df_Empaquetamiento_filtrado_geografia = df_Empaquetamiento_filtrado_geografia
    if selected_municipios:
        df_Empaquetamiento_filtrado_geografia = df_Empaquetamiento_filtrado_geografia[df_Empaquetamiento_filtrado_geografia['MUNICIPIO'].isin(selected_municipios)]
    return df_Empaquetamiento_filtrado_geografia

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)