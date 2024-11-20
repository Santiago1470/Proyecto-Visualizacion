import dash
from dash import dash_table
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import sqlite3

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

def get_db_connection():
    conn = sqlite3.connect('snies.db')
    return conn

cantidadesPrograma = """
    SELECT 
        i.nombreInstitucion as institucion,
        a.programaAcademico AS nombre_programa,
        e.genero AS sexo,
        SUM(h.inscritos) AS inscritos,
        SUM(h.matriculados) AS matriculados,
        SUM(h.admitidos) AS admitidos,
        SUM(h.graduados) AS graduados
    FROM TablaHechosSNIES h
    JOIN DimensionInstitucion i ON h.idInstitucion = i.idInstitucion
    JOIN DimensionAcademica a ON h.idAcademico = a.idAcademico
    JOIN DimensionEstudiantes e ON h.idEstudiante = e.idEstudiante
    WHERE a.nivelEducativo = 'Pregrado'
    GROUP BY i.nombreInstitucion, a.programaAcademico, e.genero;
"""

query2 = """
SELECT 
    i.nombreInstitucion as institucion,
    a.nivelEducativo AS nivel_academico,
    a.modalidad,
    SUM(h.inscritos) AS inscritos,
    SUM(h.matriculados) AS matriculados,
    SUM(h.admitidos) AS admitidos,
    SUM(h.graduados) AS graduados
FROM TablaHechosSNIES h
JOIN DimensionInstitucion i ON h.idInstitucion = i.idInstitucion
JOIN DimensionAcademica a ON h.idAcademico = a.idAcademico
GROUP BY i.nombreInstitucion, a.nivelEducativo, a.modalidad;
"""

query4 = """
SELECT 
    i.nombreInstitucion as institucion,
    a.nivelEducativo AS nivel_academico,
    e.genero AS sexo,
    SUM(h.inscritos) AS inscritos,
    SUM(h.matriculados) AS matriculados,
    SUM(h.admitidos) AS admitidos,
    SUM(h.graduados) AS graduados
FROM TablaHechosSNIES h
JOIN DimensionInstitucion i ON h.idInstitucion = i.idInstitucion
JOIN DimensionAcademica a ON h.idAcademico = a.idAcademico
JOIN DimensionEstudiantes e ON h.idEstudiante = e.idEstudiante
GROUP BY i.nombreInstitucion, a.nivelEducativo, e.genero;
"""

query_map = """
SELECT 
    i.nombreInstitucion as institucion,
    d.codigoDepartamento AS codigo_departamento,
    d.nombreDepartamento AS nombre_departamento,
    SUM(h.inscritos) AS inscritos,
    SUM(h.matriculados) AS matriculados,
    SUM(h.admitidos) AS admitidos,
    SUM(h.graduados) AS graduados
FROM TablaHechosSNIES h
JOIN DimensionInstitucion i ON h.idInstitucion = i.idInstitucion
JOIN DimensionDepartamento d ON i.idInstitucionDpto = d.idDepartamento
GROUP BY i.nombreInstitucion, d.codigoDepartamento, d.nombreDepartamento;
"""

app.layout = html.Div([
    html.H1("Proyecto Final - Visualización de Datos Educativos", 
            style={'textAlign': 'center', 'padding': '20px', 'color': '#343a40'}),
    
    html.Div([
        # Filtro por Institución
        html.Div([
            html.H3("Seleccionar Institución", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Dropdown(
                id='institucion-dropdown',
                options=[
                    {'label': 'FUNDACION UNIVERSITARIA KONRAD LORENZ', 'value': 'FUNDACION UNIVERSITARIA KONRAD LORENZ'},
                    {'label': "UNIVERSIDAD NACIONAL DE COLOMBIA", 'value': "UNIVERSIDAD NACIONAL DE COLOMBIA"},
                    {'label': "UNIVERSIDAD DE LOS ANDES", 'value': "UNIVERSIDAD DE LOS ANDES"},
                    {'label': "UNIVERSIDAD ANTONIO NARIÑO", 'value': 'UNIVERSIDAD ANTONIO NARIÑO'},
                    {'label': "UNIVERSIDAD EXTERNADO DE COLOMBIA", "value": "UNIVERSIDAD EXTERNADO DE COLOMBIA"}
                ],
                value="FUNDACION UNIVERSITARIA KONRAD LORENZ",
                style={'margin': 'auto'}
            )
        ], style={"width": "50%", 'padding': '15px', 'margin': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px'}),
        
        # Filtro por Inscritos, Admitidos, Matriculados y Graduados
        html.Div([
            html.H3("Seleccionar Estado", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Dropdown(
                id='estado-dropdown',
                options=[
                    {'label': 'Inscritos', 'value': 'inscritos'},
                    {'label': 'Admitidos', 'value': 'admitidos'},
                    {'label': 'Matriculados', 'value': 'matriculados'},
                    {'label': 'Graduados', 'value': 'graduados'}
                ],
                value='matriculados',
                style={'margin': 'auto'}
            )
        ], style={"width": "50%", 'padding': '15px', 'margin': '10px', 'backgroundColor': '#ffffff', 'borderRadius': '10px'})
    ], style={'padding': '20px', 'backgroundColor': '#f2f2f2', "display": "flex", "flex-direction": "row"}),

    # Estadisticas en texto
    html.Div([
        html.Div(id='inscritos-text', style={'font-size': '20px', 'margin-top': '10px'}),
        html.Div(id='graduados-text', style={'font-size': '20px', 'margin-top': '10px'}),
        html.Div(id='matriculados-text', style={'font-size': '20px', 'margin-top': '10px'}),
        html.Div(id='admitidos-text', style={'font-size': '20px', 'margin-top': '10px'}),
    ], style={'padding': '20px', 'backgroundColor': '#f2f2f2', "display": "flex", "flex-direction": "row"}),

    # Primera fila de gráficas
    html.Div([
        html.Div([
            html.H3("Estudiantes por programa académico y género", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='program_geneder')
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
            html.H3("Según Modalidad y Nivel Académico (todas las universidades)", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='level-modality-dist')
        ], className='six columns', 
        style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3("Distribución por Género y Nivel Académico", style={'textAlign': 'center', 'color': '#343a40'}),
            dcc.Graph(id='gender-academic-level')
        ], className='six columns', 
        style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px'}),
    ], className='row', style={'margin': '10px'}),

    # Fila del mapa
    html.Div([
        html.Div([
            html.H3("Número de estudiantes por Departamento", style={'textAlign': 'center'}),
            dcc.Graph(id='graduates-map')
        ], className='twelve columns', style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),
    ], className='row', style={'margin': '10px'}),
    
    # Tabla
    html.Div([
        html.H1("Datos recopilados", style={'textAlign': 'center'}),
        html.Div(id='table-container')
    ])
], style={'backgroundColor': '#f2f2f2', 'padding': '20px'})

@app.callback(
    Output('program_geneder', 'figure'),
    [Input('institucion-dropdown', 'value'),
     Input('estado-dropdown', 'value')]
)
def update_program_gender(institucion, estado):
    conn = get_db_connection()
    df = pd.read_sql_query(cantidadesPrograma, conn)
    conn.close()
    
    df = df[df['institucion'] == institucion]

    fig = px.bar(
        df,
        x='nombre_programa',
        y=estado,
        color='sexo'
        # title="Graduados por programa académico"
    )
    fig.update_layout(xaxis_title="Programa Académico", yaxis_title=f"Total {estado}", xaxis=dict(tickangle=-45), height=600)
    return fig

@app.callback(
    Output('program-distribution', 'figure'),
    [Input('institucion-dropdown', 'value'),
     Input('estado-dropdown', 'value')]
)
def update_program_distribution(institucion, estado):
    conn = get_db_connection()
    df = pd.read_sql_query(cantidadesPrograma, conn)
    conn.close()
    
    # Filtrar por institución
    df = df[df['institucion'] == institucion]
    
    # Ordenar por 'estado' y seleccionar los 10 primeros
    df = df.sort_values(by=estado, ascending=False)
    top_programs = df.head(10)
    
    # Calcular la suma de los valores restantes como "Otros"
    others_sum = df[estado].iloc[10:].sum()
    if others_sum > 0:
        top_programs = pd.concat([
            top_programs,
            pd.DataFrame({'nombre_programa': ['Otros'], estado: [others_sum]})
        ])
    
    # Crear gráfico de pie
    fig = px.pie(
        top_programs,
        values=estado,
        names='nombre_programa',
        title=f"Distribución por Programa Académico ({institucion})"
    )
    fig.update_layout(height=600)
    
    return fig


# Callback: Inscritos y Matriculados por Modalidad y Nivel
@app.callback(
    Output('level-modality-dist', 'figure'),
    [Input('institucion-dropdown', 'value'),
    Input('estado-dropdown', 'value')]
)
def update_level_modality_distribution(institucion, estado):
    conn = get_db_connection()
    df = pd.read_sql_query(query2, conn)
    conn.close()
    
    # df = df[df['institucion'] == institucion]
    df = df[df['modalidad'] != "Sin información"]
    # print(df)
    fig = px.bar(
        df,
        x='nivel_academico',
        y=estado,
        color='modalidad',
        barmode='stack'
        # title="Inscritos y Matriculados por Modalidad y Nivel Académico"
    )
    fig.update_layout(xaxis_title="Nivel Académico", yaxis_title="Total")
    return fig


# Callback: Distribución por Género y Nivel Académico
@app.callback(
    Output('gender-academic-level', 'figure'),
    [Input('institucion-dropdown', 'value'),
    Input('estado-dropdown', 'value')]
)
def update_gender_academic_level(institucion, estado):
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query4, conn)
    finally:
        conn.close()
        
    df = df[df['institucion'] == institucion]
    df = df[df['nivel_academico'] != "Sin información"]
    # print(df)
    # print(estado)
    fig = px.bar(
        df,
        x='nivel_academico',
        y=estado,
        color='sexo',
        barmode='group'
        # title="Graduados por Género y Nivel Académico"
    )
    fig.update_layout(xaxis_title="Nivel Académico", yaxis_title="Total Graduados")
    return fig

# Callback: Mapa de Graduados por Departamento
@app.callback(
    Output('graduates-map', 'figure'),
    [Input('institucion-dropdown', 'value'),
    Input('estado-dropdown', 'value')]
)
def update_graduates_map(institucion, estado):
    conn = get_db_connection()
    df = pd.read_sql_query(query_map, conn)
    conn.close()
    
    df = df[df['institucion'] == institucion]
    print(df)
    fig = px.choropleth(
        df,
        geojson="https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json",
        locations="codigo_departamento",
        featureidkey="properties.DPTO",
        color=estado,
        hover_name="nombre_departamento",
        color_continuous_scale="Jet",
        labels={estado: estado}
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        # title_text=f'Número de {estado} por Departamento en Colombia',
        coloraxis_colorbar=dict(
            title=estado
        )
    )
    return fig

@app.callback(
    Output('table-container', 'children'),
    Input('institucion-dropdown', 'value')
)
def update_table(institucion):
    conn = get_db_connection()
    df = pd.read_sql_query(cantidadesPrograma, conn)
    conn.close()

    df = df[df['institucion'] == institucion]

    table = dash_table.DataTable(
        id='data-table',
        columns=[
            {"name": col, "id": col} for col in df.columns
        ],
        data=df.to_dict('records'),
        style_table={'height': '400px', 'overflowY': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '10px'},
        style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold'},
    )
    
    return table

@app.callback(
    [Output('inscritos-text', 'children'),
     Output('graduados-text', 'children'),
     Output('matriculados-text', 'children'),
     Output('admitidos-text', 'children')],
    [Input('institucion-dropdown', 'value')]
)
def update_metrics(institucion):
    conn = get_db_connection()
    df = pd.read_sql_query(cantidadesPrograma, conn)
    conn.close()

    if institucion:
        df = df[df['institucion'] == institucion]
    
    total_inscritos = df['inscritos'].sum()
    total_graduados = df['graduados'].sum()
    total_matriculados = df['matriculados'].sum()
    total_admitidos = df['admitidos'].sum()
    
    return (
        f"Total Inscritos: {total_inscritos}",
        f"Total Graduados: {total_graduados}",
        f"Total Matriculados: {total_matriculados}",
        f"Total Admitidos: {total_admitidos}"
    )

if __name__ == '__main__':
    app.run_server(debug=True)

# Hecho por:
# Óscar Julian Ramirez Contreras
# Santiago Jair Torres Rivera