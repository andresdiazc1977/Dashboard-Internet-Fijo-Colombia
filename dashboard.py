import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import pandas as pd

# Cargar plantilla
load_figure_template('MINTY')

# Crear la aplicación Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])


# Carga de datasets
df_Accesos = pd.read_csv('https://postdata.gov.co/sites/default/files/datasets/data/ACCESOS_INTERNET_FIJO_2_20.csv', delimiter=';') 
df_Accesos['VELOCIDAD_EFECTIVA_DOWNSTREAM'] = pd.to_numeric(df_Accesos['VELOCIDAD_EFECTIVA_DOWNSTREAM'], errors='coerce')
df_Accesos['VELOCIDAD_EFECTIVA_UPSTREAM'] = pd.to_numeric(df_Accesos['VELOCIDAD_EFECTIVA_UPSTREAM'], errors='coerce')

# Obtener el mayor año y trimestre dentro de ese año para establecerlo por defecto en los filtros
ultimo_anno = df_Accesos['ANNO'].max()
ultimo_trimestre = df_Accesos[df_Accesos['ANNO'] == ultimo_anno]['TRIMESTRE'].max()

# Layout de la aplicación
app.layout = html.Div(children = [
    dbc.Row(
        [
            dbc.Col(html.H1('Indicadores de Internet Fijo en Colombia', className='bg-primary text-white p-2 mb-3'),)
        ]
        ),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Row(html.H6('Filtros', className='bg-primary text-white p-2 mb-3'),
                        ),
                    dbc.Row(
                            html.Div(['Seleccione un año',
                                      dcc.Dropdown(id='anno-dropdown', options=[{'label': anno, 'value': anno} for anno in df_Accesos['ANNO'].unique()], value=ultimo_anno,)
                                      ]),
                        
                        ),
                    dbc.Row(
                            html.Div(['Seleccione un trimestre',
                                      dcc.Dropdown(id='trimestre-dropdown',options=[{'label': trimestre, 'value': trimestre} for trimestre in df_Accesos['TRIMESTRE'].unique()],value=ultimo_trimestre,)
                                      ]),
                        
                        ),
                ], lg=2),
            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(dcc.Graph(id='total-accesos-gauge', className='border'), lg=2),
                            dbc.Col(dcc.Graph(id='velocidad-promedio-gauge', className='border'), lg=2),
                        ],
                        className="mt-4",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(dcc.Graph(id='top-10-accesos-empresa', className='border'), lg=5),
                            dbc.Col(dcc.Graph(id='top-10-porcentaje-empresa', className='border'), lg=5),
                        ],
                        className="mt-4",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(dcc.Graph(id='velocidades_histograma', className='border'), lg=5),
                            dbc.Col(dcc.Graph(id='tecnologias_pie', className='border'), lg=5),
                        ],
                        className="mt-4",
                    ),
                ], lg=10),
        ],
    )
])

# Callback para actualizar las gráficas cuando se cambian los filtros
@app.callback(
    [Output('total-accesos-gauge', 'figure'),
     Output('velocidad-promedio-gauge', 'figure'),
     Output('top-10-accesos-empresa', 'figure'),
     Output('top-10-porcentaje-empresa', 'figure'),
     Output('velocidades_histograma', 'figure'),
     Output('tecnologias_pie', 'figure')],
    [Input('anno-dropdown', 'value'),
     Input('trimestre-dropdown', 'value')]
)

# Filtrado de los datasets
def update_graphs(anno, trimestre):
    filtered_df_Accesos = df_Accesos[(df_Accesos['ANNO'] == anno) & (df_Accesos['TRIMESTRE'] == trimestre)]
    
   
# Gráfico de medidor con el total de accesos
    total_accesos = filtered_df_Accesos['ACCESOS'].sum()
    total_accesos_gauge = go.Figure(go.Indicator(
        mode = 'gauge+number',
        value = total_accesos,
        title = {'text': 'Total de Accesos'},
        gauge = {'axis': {'range': [None, 10000000]},
                 'steps' : [
                     {'range': [0, 2000000], 'color': 'gainsboro'},
                     {'range': [2000000, 4000000], 'color': 'lightgrey'},
                     {'range': [4000000, 6000000], 'color': 'lightgray'},
                     {'range': [6000000, 8000000], 'color': 'silver'}],
                 'threshold' : {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': 9990000}}
    ))

# Gráfico de medidor con el promedio de velocidad de descarga
    velocidad = (filtered_df_Accesos['VELOCIDAD_EFECTIVA_DOWNSTREAM']*filtered_df_Accesos['ACCESOS']).sum()
    promedio_velocidad = velocidad/total_accesos
    velocidad_promedio_gauge = go.Figure(go.Indicator(
        mode = 'gauge+number',
        value = promedio_velocidad,
        title = {'text': 'Promedio Velocidad Downstream (Mbps)'},
        gauge = {'axis': {'range': [None, 1000]},
                 'steps' : [
                     {'range': [0, 200], 'color': 'gainsboro'},
                     {'range': [200, 400], 'color': 'lightgrey'},
                     {'range': [400, 600], 'color': 'lightgray'},
                     {'range': [600, 800], 'color': 'silver'}],
                 'threshold' : {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': 990}}
    ))
   
# Gráfico de barras con el top 10 de la suma de accesos por empresa
    filtered_df_Accesos2 = filtered_df_Accesos.copy()
    top_10_empresas = filtered_df_Accesos2.groupby('EMPRESA')['ACCESOS'].sum().sort_values(ascending=False).reset_index()
    top_10_empresas = top_10_empresas.sort_values('ACCESOS', ascending=False).head(10)
    top_10_nombres = top_10_empresas['EMPRESA'].tolist()
    filtered_df_Accesos2['EMPRESA_TOP10'] = filtered_df_Accesos2['EMPRESA'].apply(lambda x: x if x in top_10_nombres else 'OTROS')
    top_10_empresas = filtered_df_Accesos2.groupby('EMPRESA_TOP10')['ACCESOS'].sum().reset_index()
    top_10_empresas.rename(columns = {'EMPRESA_TOP10':'EMPRESA'}, inplace = True)
    top_10_accesos_empresa = px.bar(top_10_empresas, y='EMPRESA', x='ACCESOS', orientation='h', template="MINTY",
                                    title='Accesos por Empresa (Top 10)', labels={'ACCESOS': 'Accesos'})
    top_10_accesos_empresa.update_layout(yaxis={'categoryorder': 'total ascending'})  # Ordena las barras por valor

# Gráfico de pie con el top 10 del porcentaje del total por empresa
    top_10_empresas['Porcentaje'] = top_10_empresas['ACCESOS'] / total_accesos * 100
    top_10_pie = px.pie(top_10_empresas, values='Porcentaje', names='EMPRESA', template='MINTY', title='Top 10 Participación de Mercado (Top 10)')
    
# Histograma de Velocidades de descarga
    filtered_df_Accesos4 = filtered_df_Accesos.copy()
    etiquetas_velocidad = ['0-10', '10-50', '50-100', '100-500', '500-100', '>1000']
    bordes_velocidad = [0, 10, 50, 100, 500, 1000, 5000]
    filtered_df_Accesos4['VELOCIDAD'] = pd.cut(filtered_df_Accesos4['VELOCIDAD_EFECTIVA_DOWNSTREAM'], bins=bordes_velocidad, labels=etiquetas_velocidad)
    velocidades = filtered_df_Accesos4.groupby('VELOCIDAD')['ACCESOS'].sum().reset_index()
    #velocidades_histograma = px.histogram(velocidades, x='VELOCIDAD_EFECTIVA_DOWNSTREAM', nbins=25, template='MINTY', title='Velocidades de Descarga')
    velocidades_histograma = px.bar(velocidades, x='VELOCIDAD', y='ACCESOS', template='MINTY', title='Velocidades de Descarga')

# Gráfico de pie con tecnologias de conexion
    filtered_df_Accesos3 = filtered_df_Accesos.copy()
    top_10_tecnologias = filtered_df_Accesos3.groupby('TECNOLOGIA')['ACCESOS'].sum().sort_values(ascending=False).reset_index()
    top_10_tecnologias = top_10_tecnologias.sort_values('ACCESOS', ascending=False).head(10)
    top_10_nombres_tec = top_10_tecnologias['TECNOLOGIA'].tolist()
    filtered_df_Accesos3['TECNOLOGIA_TOP10'] = filtered_df_Accesos3['TECNOLOGIA'].apply(lambda x: x if x in top_10_nombres_tec else 'Otras')
    top_10_tecnologias = filtered_df_Accesos3.groupby('TECNOLOGIA_TOP10')['ACCESOS'].sum().reset_index()
    top_10_tecnologias.rename(columns = {'TECNOLOGIA_TOP10':'TECNOLOGIA'}, inplace = True)
    top_10_tecnologias['Porcentaje'] = top_10_tecnologias['ACCESOS'] / total_accesos * 100
    tecnologias_pie = px.pie(top_10_tecnologias, values='Porcentaje', names='TECNOLOGIA', template='MINTY',title='Tecnología de Conexión')
        
    return total_accesos_gauge, velocidad_promedio_gauge, top_10_accesos_empresa, top_10_pie, velocidades_histograma, tecnologias_pie 

# Ejecutar la aplicación Dash
if __name__ == '__main__':
    app.run_server(debug=True)