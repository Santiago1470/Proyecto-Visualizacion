import dash
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

# Consultas actualizadas
query1 = """
SELECT  p.nombre_programa,
SUM(he.inscritos) AS total_inscritos,
SUM(he.matriculados) AS total_matriculados,
SUM(he.admitidos) AS total_admitidos,
SUM(he.graduados) AS total_graduados
FROM HECHOS_EDUCACION he
JOIN PROGRAMA p ON he.id_programa = p.id_programa
join NIVEL n on he.id_nivel  = n.id_nivel 
where n.nivel_academico = 'Pregrado'
GROUP BY p.nombre_programa;
"""

query2 = """
SELECT n.nivel_academico, n.modalidad, 
       SUM(he.inscritos) AS total_inscritos, 
       SUM(he.matriculados) AS total_matriculados 
FROM HECHOS_EDUCACION he
JOIN NIVEL n ON he.id_nivel = n.id_nivel
GROUP BY n.nivel_academico, n.modalidad;
"""

query3 = """
SELECT p.area_conocimiento, i.sector_ies,
       SUM(he.graduados) AS total_graduados
FROM HECHOS_EDUCACION he
JOIN PROGRAMA p ON he.id_programa = p.id_programa
JOIN INSTITUCION i ON he.id_institucion = i.id_institucion
WHERE p.area_conocimiento != 'Sin información'
GROUP BY p.area_conocimiento, i.sector_ies;
"""

query4 = """
SELECT n.nivel_academico, d.sexo,
       SUM(he.admitidos) AS total_admitidos,
       SUM(he.graduados) AS total_graduados
FROM HECHOS_EDUCACION he
JOIN NIVEL n ON he.id_nivel = n.id_nivel
JOIN DEMOGRAFICO d ON he.id_demografico = d.id_demografico
GROUP BY n.nivel_academico, d.sexo;
"""

query5 = """
SELECT n.nivel_academico, p.area_conocimiento,
       SUM(he.inscritos) AS total_inscritos
FROM HECHOS_EDUCACION he
JOIN NIVEL n ON he.id_nivel = n.id_nivel
JOIN PROGRAMA p ON he.id_programa = p.id_programa
WHERE p.area_conocimiento != 'Sin información'
GROUP BY n.nivel_academico, p.area_conocimiento;
"""

query6 = """
SELECT p.area_conocimiento,
       SUM(he.admitidos) AS total_admitidos,
       SUM(he.graduados) AS total_graduados
FROM HECHOS_EDUCACION he
JOIN PROGRAMA p ON he.id_programa = p.id_programa
JOIN NIVEL n ON he.id_nivel = n.id_nivel
WHERE p.area_conocimiento != 'Sin información'
GROUP BY p.area_conocimiento;
"""

query7 = """
SELECT p.area_conocimiento, d.sexo,
       SUM(he.graduados) AS total_graduados
FROM HECHOS_EDUCACION he
JOIN PROGRAMA p ON he.id_programa = p.id_programa
JOIN DEMOGRAFICO d ON he.id_demografico = d.id_demografico
GROUP BY p.area_conocimiento, d.sexo;
"""

# Layout del dashboard
app.layout = html.Div([  # Ya está configurado
    html.H1("Dashboard Educativo de Colombia", style={'textAlign': 'center', 'padding': '20px'}),
    
    # Primer fila
    html.Div([
        html.Div([html.H3("Distribución por Programa Académico", style={'textAlign': 'center'}), dcc.Graph(id='program-distribution')], className='twelve columns', style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),
    ], className='row', style={'margin': '10px'}),
    
    # Segunda fila
    html.Div([
        html.Div([html.H3("Inscritos y Matriculados por Modalidad y Nivel", style={'textAlign': 'center'}), dcc.Graph(id='level-modality-dist')], className='six columns', style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),
        html.Div([html.H3("Graduados por Área y Sector", style={'textAlign': 'center'}), dcc.Graph(id='graduates-area-sector')], className='six columns', style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),
    ], className='row', style={'margin': '10px'}),
    
    # Tercera fila
    html.Div([
        html.Div([html.H3("Distribución por Género y Nivel Académico", style={'textAlign': 'center'}), dcc.Graph(id='gender-academic-level')], className='six columns', style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),
        html.Div([html.H3("Inscritos por Área de Conocimiento", style={'textAlign': 'center'}), dcc.Graph(id='enrollees-knowledge-area')], className='six columns', style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),
    ], className='row', style={'margin': '10px'}),
    
    # Cuarta fila
    html.Div([
        html.Div([html.H3("Admitidos y Graduados por Área", style={'textAlign': 'center'}), dcc.Graph(id='admitted-graduated-area')], className='six columns', style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),
        html.Div([html.H3("Graduados por Género y Área", style={'textAlign': 'center'}), dcc.Graph(id='graduates-gender-area')], className='six columns', style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),
    ], className='row', style={'margin': '10px'}),
], style={'backgroundColor': '#f2f2f2', 'padding': '20px'})


if __name__ == '__main__':
    app.run_server(debug=True)

@app.callback(
    Output('level-modality-dist', 'figure'),
    Input('level-modality-dist', 'id')
)
def update_level_modality_dist(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query2, conn)
    conn.close()
    
    fig = px.sunburst(
        df,
        path=['nivel_academico', 'modalidad'],
        values='total_inscritos',
        color='total_matriculados',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

# Callback para 'graduates-area-sector'
@app.callback(
    Output('graduates-area-sector', 'figure'),
    Input('graduates-area-sector', 'id')
)
def update_graduates_area_sector(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query3, conn)
    conn.close()
    
    fig = px.treemap(
        df,
        path=[px.Constant("Todos"), 'area_conocimiento', 'sector_ies'],
        values='total_graduados',
        color='total_graduados',
        color_continuous_scale='RdBu'
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

# Callback para 'gender-academic-level'
@app.callback(
    Output('gender-academic-level', 'figure'),
    Input('gender-academic-level', 'id')
)
def update_gender_academic_level(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query4, conn)
    conn.close()
    
    fig = px.bar(
        df,
        x='nivel_academico',
        y=['total_admitidos', 'total_graduados'],
        color='sexo',
        barmode='group',
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

# Callback para 'enrollees-knowledge-area'
@app.callback(
    Output('enrollees-knowledge-area', 'figure'),
    Input('enrollees-knowledge-area', 'id')
)
def update_enrollees_knowledge_area(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query5, conn)
    conn.close()
    
    fig = px.treemap(
        df,
        path=[px.Constant("Todos"), 'nivel_academico', 'area_conocimiento'],
        values='total_inscritos',
        color='total_inscritos',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

# Callback para 'admitted-graduated-area'
@app.callback(
    Output('admitted-graduated-area', 'figure'),
    Input('admitted-graduated-area', 'id')
)
def update_admitted_graduated_area(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query6, conn)
    conn.close()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Admitidos',
        x=df['area_conocimiento'],
        y=df['total_admitidos'],
        marker_color='#1f77b4'
    ))
    fig.add_trace(go.Bar(
        name='Graduados',
        x=df['area_conocimiento'],
        y=df['total_graduados'],
        marker_color='#2ca02c'
    ))
    
    fig.update_layout(
        barmode='group',
        xaxis_tickangle=-45,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

# Callback para 'graduates-gender-area'
@app.callback(
    Output('graduates-gender-area', 'figure'),
    Input('graduates-gender-area', 'id')
)
def update_graduates_gender_area(dummy):
    conn = get_db_connection()
    df = pd.read_sql_query(query7, conn)
    conn.close()
    
    fig = px.sunburst(
        df,
        path=['area_conocimiento', 'sexo'],
        values='total_graduados',
        color='total_graduados',
        color_continuous_scale='RdBu'
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig
