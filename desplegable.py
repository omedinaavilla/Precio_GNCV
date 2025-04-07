import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
import geopandas as gpd
import json

# === CARGAR DATOS ===
df = pd.read_csv("df_limpio.csv")
df["FECHA_PRECIO"] = pd.to_datetime(df["FECHA_PRECIO"])

# Shapefile de departamentos
gdf = gpd.read_file("departamentos.geojson")
gdf['DPTO_CNMBR'] = gdf['DPTO_CNMBR'].str.upper().str.strip()

# Promedio de precios por departamento
df_dep = df.groupby('DEPARTAMENTO_EDS')['PRECIO_PROMEDIO_PUBLICADO'].mean().reset_index()
df_dep['DEPARTAMENTO_EDS'] = df_dep['DEPARTAMENTO_EDS'].str.upper().str.strip()
gdf_merged = gdf.merge(df_dep, left_on='DPTO_CNMBR', right_on='DEPARTAMENTO_EDS')
geojson = json.loads(gdf_merged.to_json())

# === GRÁFICAS ===
df_filtrado = df[df['PRECIO_PROMEDIO_PUBLICADO'].between(1000, 4000)]
fig_hist = px.histogram(
    df_filtrado,
    x='PRECIO_PROMEDIO_PUBLICADO',
    nbins=40,
    title='Distribución del Precio Promedio Publicado (1000 - 4000)',
    template='plotly_white',
    color_discrete_sequence=['#3b82f6']
)
fig_hist.update_layout(bargap=0.05)

# Línea de tendencia mensual
df_mes = df.copy()
df_mes['AÑO_MES'] = df_mes['FECHA_PRECIO'].dt.to_period('M').astype(str)
linea_global = df_mes.groupby('AÑO_MES')['PRECIO_PROMEDIO_PUBLICADO'].mean().reset_index()
fig_linea = px.line(
    linea_global,
    x='AÑO_MES',
    y='PRECIO_PROMEDIO_PUBLICADO',
    title='Tendencia del Precio Promedio de GNCV en el Tiempo',
    template='plotly_white'
)
fig_linea.update_traces(line_color='#1e3a8a')
fig_linea.update_layout(xaxis_tickangle=45)

# Boxplot por departamento
fig_box = px.box(
    df[df['PRECIO_PROMEDIO_PUBLICADO'] < 5000],
    x='DEPARTAMENTO_EDS',
    y='PRECIO_PROMEDIO_PUBLICADO',
    title='Distribución de Precios por Departamento',
    template='plotly_white',
    color_discrete_sequence=['#6366f1']
)
fig_box.update_layout(xaxis_tickangle=45)

# === DASH APP ===
app = dash.Dash(__name__)
app.title = "Análisis de GNCV"

# Tabla de variables
tabla_variables = pd.DataFrame({
    "Variable": [
        "FECHA_PRECIO", "ANIO_PRECIO, MES_PRECIO, DIA_PRECIO", "DEPARTAMENTO_EDS",
        "MUNICIPIO_EDS", "NOMBRE_COMERCIAL_EDS", "PRECIO_PROMEDIO_PUBLICADO",
        "TIPO_COMBUSTIBLE", "CODIGO_MUNICIPIO_DANE", "LATITUD_MUNICIPIO, LONGITUD_MUNICIPIO"
    ],
    "Descripción": [
        "Fecha del reporte del precio",
        "Año, mes y día del reporte (útil para agrupar por tiempo)",
        "Departamento donde está ubicada la estación",
        "Municipio de la estación de servicio",
        "Nombre de la estación de servicio",
        "Precio promedio del GNCV publicado en esa estación (en pesos)",
        "Tipo de combustible (GNCV en todos los casos)",
        "Código DANE del municipio (útil para georreferenciar)",
        "Coordenadas geográficas del municipio"
    ]
})

app.layout = html.Div(style={'backgroundColor': '#f8fafc', 'color': '#1f2937'}, children=[
    html.H1("🔍 ANÁLISIS DE PRECIO DE GNCV EN COLOMBIA", style={'textAlign': 'center', 'backgroundColor': '#1e3a8a', 'color': 'white', 'padding': '15px'}),

    dcc.Tabs(style={
        'backgroundColor': '#e2e8f0',
        'color': '#1e293b',
        'fontWeight': 'bold'
    },
    children=[ 
        dcc.Tab(label='📘 Contexto', style={'backgroundColor': '#f8fafc'}, selected_style={'color': '#1e293b', 'fontWeight': 'bold', 'backgroundColor': '#cbd5e1'}, children=[
            html.Div(style={'padding': '40px', 'fontFamily': 'Arial'}, children=[
                html.H2("VISIÓN GENERAL", style={'textAlign': 'center', 'marginBottom': '20px'}),
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '60px', 'justifyContent': 'space-around'}, children=[
                    html.Img(src='/assets/query (1).png', style={'height': '300px'}),
                    html.Div(children=[
                        html.P("Esta base de datos contiene registros históricos del precio promedio del Gas Natural Comprimido Vehicular (GNCV) por estación de servicio en Colombia. Incluye información como el nombre de la estación, municipio, departamento, coordenadas geográficas, tipo de combustible y fechas asociadas al precio reportado. Los datos son recolectados y consolidados por el Sistema de Información de Combustibles (SICOM).", style={'fontSize': '16px', 'marginBottom': '20px'}),
                        html.P("Fuente: Ministerio de Minas y Energía – Sistema SICOM", style={'fontSize': '16px'}),
                        html.P("Actualización: 28 de Marzo de 2025", style={'fontSize': '16px'}),
                        html.P("Registros: {:,}".format(df.shape[0]), style={'fontSize': '16px'}),
                        html.P("Cobertura: Nacional", style={'fontSize': '16px'})
                    ]),
                    html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}, children=[
                        html.Div(style={'backgroundColor': '#1e3a8a', 'color': 'white', 'padding': '15px', 'borderRadius': '50%', 'width': '120px', 'height': '120px', 'textAlign': 'center', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}, children=[
                            html.Div("PROMEDIO", style={'fontSize': '12px'}),
                            html.Div("{:.2f}".format(df['PRECIO_PROMEDIO_PUBLICADO'].mean()), style={'fontSize': '20px', 'fontWeight': 'bold'})
                        ]),
                        html.Div(style={'backgroundColor': '#15803d', 'color': 'white', 'padding': '15px', 'borderRadius': '50%', 'width': '120px', 'height': '120px', 'textAlign': 'center', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}, children=[
                            html.Div("EDS", style={'fontSize': '12px'}),
                            html.Div("{:.0f}".format(df['NOMBRE_COMERCIAL_EDS'].nunique()), style={'fontSize': '20px', 'fontWeight': 'bold'})
                        ])
                    ])
                ])
            ])
        ]),
        dcc.Tab(label='📊 Análisis Exploratorio', style={'backgroundColor': '#f8fafc'}, selected_style={'color': '#1e293b', 'fontWeight': 'bold', 'backgroundColor': '#cbd5e1'}, children=[
            html.Div(style={'padding': '30px'}, children=[
                dcc.Graph(figure=fig_hist),
                dcc.Graph(figure=fig_linea),
                dcc.Graph(figure=fig_box)
            ])
        ]),
        dcc.Tab(label='🗺️ Mapa Interactivo', style={'backgroundColor': '#f8fafc'}, selected_style={'color': '#1e293b', 'fontWeight': 'bold', 'backgroundColor': '#cbd5e1'}, children=[
            html.Div(style={'padding': '30px'}, children=[
                html.Label("Selecciona un departamento para filtrar:"),
                dcc.Dropdown(
                    id='departamento-dropdown',
                    options=[{'label': dpto, 'value': dpto} for dpto in sorted(gdf_merged['DEPARTAMENTO_EDS'].unique())],
                    value=None,
                    placeholder="Todos los departamentos"
                ),
                dcc.Graph(id='choropleth-map')
            ])
        ]),
        dcc.Tab(label='📄 Variables', style={'backgroundColor': '#f8fafc'}, selected_style={'color': '#1e293b', 'fontWeight': 'bold', 'backgroundColor': '#cbd5e1'}, children=[
            html.Div(style={'padding': '40px'}, children=[
                html.H2("Variables de la Base de Datos", style={'textAlign': 'center', 'marginBottom': '30px'}),
                dash_table.DataTable(
                    columns=[{"name": i, "id": i} for i in tabla_variables.columns],
                    data=tabla_variables.to_dict('records'),
                    style_table={'margin': '0 auto', 'maxWidth': '800px'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'fontWeight': 'bold', 'backgroundColor': '#1e3a8a', 'color': 'white'},
                    style_data={'backgroundColor': '#f1f5f9'}
                )
            ])
        ])
    ])
])

@app.callback(
    dash.dependencies.Output('choropleth-map', 'figure'),
    [dash.dependencies.Input('departamento-dropdown', 'value')]
)
def actualizar_mapa(departamento):
    if departamento:
        gdf_filtrado = gdf_merged[gdf_merged['DEPARTAMENTO_EDS'] == departamento]
    else:
        gdf_filtrado = gdf_merged
    geojson_filtrado = json.loads(gdf_filtrado.to_json())

    fig = px.choropleth(
        gdf_filtrado,
        geojson=geojson_filtrado,
        locations=gdf_filtrado.index,
        color='PRECIO_PROMEDIO_PUBLICADO',
        hover_name='DEPARTAMENTO_EDS',
        color_continuous_scale="Viridis",
        title="Precio Promedio Publicado de GNCV por Departamento"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(template="plotly_dark")
    return fig

# Ejecutar app
if __name__ == '__main__':
    app.run(debug=True)

server = app.server
