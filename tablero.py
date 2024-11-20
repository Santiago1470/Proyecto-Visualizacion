import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import sqlite3
# Configuración inicial de la aplicación
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

def get_db_connection():
    # Conexión a la base de datos
    conn = sqlite3.connect('snies.db')  # Asegúrate de tener la base en la ruta correcta
    return conn

# Consultas SQL ajustadas al esquema de la base de datos
query1 = """
SELECT 
    a.programaAcademico AS nombre_programa,
    SUM(h.inscritos) AS total_inscritos,
    SUM(h.matriculados) AS total_matriculados,
    SUM(h.admitidos) AS total_admitidos,
    SUM(h.graduados) AS total_graduados
FROM TablaHechosSNIES h
JOIN DimensionAcademica a ON h.idAcademico = a.idAcademico
WHERE a.nivelEducativo = 'Pregrado'
GROUP BY a.programaAcademico;
"""

query2 = """
SELECT 
    a.nivelEducativo AS nivel_academico,
    a.modalidad,
    SUM(h.inscritos) AS total_inscritos,
    SUM(h.matriculados) AS total_matriculados
FROM TablaHechosSNIES h
JOIN DimensionAcademica a ON h.idAcademico = a.idAcademico
GROUP BY a.nivelEducativo, a.modalidad;
"""

query3 = """
SELECT 
    a.programaAcademico AS area_conocimiento,
    i.tipoInstitucion AS sector_ies,
    SUM(h.graduados) AS total_graduados
FROM TablaHechosSNIES h
JOIN DimensionAcademica a ON h.idAcademico = a.idAcademico
JOIN DimensionInstitucion i ON h.idInstitucion = i.idInstitucion
GROUP BY a.programaAcademico, i.tipoInstitucion;
"""

query4 = """
SELECT 
    a.nivelEducativo AS nivel_academico,
    e.genero AS sexo,
    SUM(h.graduados) AS total_graduados
FROM TablaHechosSNIES h
JOIN DimensionAcademica a ON h.idAcademico = a.idAcademico
JOIN DimensionEstudiantes e ON h.idEstudiante = e.idEstudiante
GROUP BY a.nivelEducativo, e.genero;
"""

query5 = """
SELECT 
    a.nivelEducativo AS nivel_academico,
    a.programaAcademico AS area_conocimiento,
    SUM(h.inscritos) AS total_inscritos
FROM TablaHechosSNIES h
JOIN DimensionAcademica a ON h.idAcademico = a.idAcademico
GROUP BY a.nivelEducativo, a.programaAcademico;
"""

query6 = """
SELECT 
    a.programaAcademico AS area_conocimiento,
    SUM(h.admitidos) AS total_admitidos,
    SUM(h.graduados) AS total_graduados
FROM TablaHechosSNIES h
JOIN DimensionAcademica a ON h.idAcademico = a.idAcademico
GROUP BY a.programaAcademico;
"""

query7 = """
SELECT 
    a.programaAcademico AS area_conocimiento,
    d.sexo,
    SUM(h.graduados) AS total_graduados
FROM TablaHechosSNIES h
JOIN DimensionAcademica a ON h.idAcademico = a.idAcademico
JOIN DimensionDemografica d ON h.idDemografico = d.idDemografico
GROUP BY a.programaAcademico, d.sexo;
"""

query_map = """
SELECT 
    d.codigoDepartamento AS codigo_departamento,
    d.nombreDepartamento AS nombre_departamento,
    SUM(h.graduados) AS total_graduados
FROM TablaHechosSNIES h
JOIN DimensionInstitucion i ON h.idInstitucion = i.idInstitucion
JOIN DimensionDepartamento d ON i.idInstitucionDpto = d.idDepartamento
GROUP BY d.codigoDepartamento, d.nombreDepartamento;
"""
# Layout de la aplicación
app.layout = html.Div([
    html.H1("Proyecto Final - Visualización de Datos Educativos", 
            style={'textAlign': 'center', 'padding': '20px', 'color': '#343a40'}),
    
    # Primera fila de gráficas
    html.Div([
        html.Div([
            html.H3("Graduados por Área y Sector", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='graduates-area-sector')
        ], className='six columns', 
        style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3("Distribución por Programa Académico", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='program-distribution')
        ], className='six columns', 
        style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px'}),
    ], className='row', style={'margin': '10px'}),
    
    # Segunda fila de gráficas
    html.Div([
        html.Div([
            html.H3("Inscritos y Matriculados por Modalidad y Nivel", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='level-modality-dist')
        ], className='six columns', 
        style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3("Distribución por Género y Nivel Académico", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='gender-academic-level')
        ], className='six columns', 
        style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px'}),
    ], className='row', style={'margin': '10px'}),
    
    # Tercera fila de gráficas
    html.Div([
        html.Div([
            html.H3("Admitidos y Graduados por Área", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='admitted-graduated-area')
        ], className='six columns', 
        style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3("Inscritos por Área de Conocimiento", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='enrollees-knowledge-area')
        ], className='six columns', 
        style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px'}),
    ], className='row', style={'margin': '10px'}),
    
    # Cuarta fila
    html.Div([
        html.Div([
            html.H3("Número de Graduados por Departamento", style={'textAlign': 'center'}),
            dcc.Graph(id='graduates-map')
        ], className='twelve columns', style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),
    ], className='row', style={'margin': '10px'}),
], style={'backgroundColor': '#f2f2f2', 'padding': '20px'})

# Callback: Gráfica de Graduados por Área y Sector
@app.callback(
    Output('graduates-area-sector', 'figure'),
    Input('graduates-area-sector', 'id')
)
def update_graduates_area_sector(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query3, conn)
    conn.close()

    fig = px.bar(
        df,
        x='area_conocimiento',
        y='total_graduados',
        color='sector_ies',
        barmode='group',
        title="Graduados por Área y Sector"
    )
    fig.update_layout(xaxis_title="Área de Conocimiento", yaxis_title="Total Graduados")
    return fig


# Callback: Distribución por Programa Académico
@app.callback(
    Output('program-distribution', 'figure'),
    Input('program-distribution', 'id')
)
def update_program_distribution(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query1, conn)
    conn.close()

    fig = px.pie(
        df,
        values='total_matriculados',
        names='nombre_programa',
        title="Distribución de Matriculados por Programa Académico"
    )
    return fig


# Callback: Inscritos y Matriculados por Modalidad y Nivel
@app.callback(
    Output('level-modality-dist', 'figure'),
    Input('level-modality-dist', 'id')
)
def update_level_modality_distribution(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query2, conn)
    conn.close()

    fig = px.bar(
        df,
        x='nivel_academico',
        y=['total_inscritos', 'total_matriculados'],
        color='modalidad',
        barmode='stack',
        title="Inscritos y Matriculados por Modalidad y Nivel Académico"
    )
    fig.update_layout(xaxis_title="Nivel Académico", yaxis_title="Total")
    return fig


# Callback: Distribución por Género y Nivel Académico
@app.callback(
    Output('gender-academic-level', 'figure'),
    Input('gender-academic-level', 'id')
)
def update_gender_academic_level(dummy):
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query4, conn)
    finally:
        conn.close()

    fig = px.bar(
        df,
        x='nivel_academico',
        y='total_graduados',
        color='sexo',
        barmode='group',
        title="Graduados por Género y Nivel Académico"
    )
    fig.update_layout(xaxis_title="Nivel Académico", yaxis_title="Total Graduados")
    return fig

# Callback: Admitidos y Graduados por Área
@app.callback(
    Output('admitted-graduated-area', 'figure'),
    Input('admitted-graduated-area', 'id')
)
def update_admitted_graduated_area(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query6, conn)
    conn.close()

    fig = px.scatter(
        df,
        x='total_admitidos',
        y='total_graduados',
        color='area_conocimiento',
        size='total_graduados',
        title="Relación entre Admitidos y Graduados por Área"
    )
    fig.update_layout(xaxis_title="Total Admitidos", yaxis_title="Total Graduados")
    return fig


# Callback: Inscritos por Área de Conocimiento
@app.callback(
    Output('enrollees-knowledge-area', 'figure'),
    Input('enrollees-knowledge-area', 'id')
)
def update_enrollees_knowledge_area(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query5, conn)
    conn.close()

    fig = px.bar(
        df,
        x='area_conocimiento',
        y='total_inscritos',
        color='nivel_academico',
        title="Inscritos por Área de Conocimiento y Nivel Académico"
    )
    fig.update_layout(xaxis_title="Área de Conocimiento", yaxis_title="Total Inscritos")
    return fig


# Callback: Mapa de Graduados por Departamento
@app.callback(
    Output('graduates-map', 'figure'),
    Input('graduates-map', 'id')
)
def update_graduates_map(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query_map, conn)
    conn.close()

    # Verificar si 'total_graduados' tiene NaN
    df['total_graduados'] = df['total_graduados'].fillna(0)
    
    # Crear el mapa
    fig = px.choropleth(
        df,
        geojson="https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json",
        locations="codigo_departamento",
        color="total_graduados",
        hover_name="nombre_departamento",
        featureidkey="properties.DPTO",  # Asegúrate de que esta clave sea correcta
        title="Número de Graduados por Departamento"
    )

    # Ajustar la visibilidad de los bordes y la proyección para el mapa de Colombia
    fig.update_geos(fitbounds="geojson", visible=True, projection_type="mercator")
    return fig

# Ejecución de la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
