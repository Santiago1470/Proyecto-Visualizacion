import sqlite3
import pandas as pd
from constant import columnas_requeridas_A, columnas_requeridas_G, columnas_requeridas_I, columnas_requeridas_M

class Database:
    def __init__(self, db_name='snies.db'):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        """Conectar a la base de datos y crear un cursor."""
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def close(self):
        """Cerrar la conexión a la base de datos."""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None
            self.cursor = None

    def create_tables(self):
        """Crear todas las tablas en la base de datos siguiendo el modelo dimensional."""
        self.connect()
        
        # Dimensión Temporal
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionTemporal (
            idTiempo INTEGER PRIMARY KEY,
            anio INTEGER,
            semestre INTEGER
        )
        ''')

        # Dimensión Estudiantes
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionEstudiantes (
            idEstudiante INTEGER PRIMARY KEY,
            genero TEXT
        )
        ''')

        # Dimensión Académica
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionAcademica (
            idAcademico INTEGER PRIMARY KEY,
            nivelEducativo TEXT,
            programaAcademico TEXT,
            modalidad TEXT
        )
        ''')

        # Dimensión Institución
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionInstitucion (
            idInstitucion INTEGER PRIMARY KEY,
            nombreInstitucion TEXT,
            tipoInstitucion TEXT,
            idInstitucionDpto INTEGER,
            FOREIGN KEY (idInstitucionDpto) REFERENCES DimensionDepartamento(idDepartamento)
        )
        ''')

        # Dimensión Departamento
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionDepartamento (
            idDepartamento INTEGER PRIMARY KEY,
            nombreDepartamento TEXT,
            codigoDepartamento TEXT
        )
        ''')

        # Dimensión Municipio
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionMunicipio (
            idMunicipio INTEGER PRIMARY KEY,
            nombreMunicipio TEXT,
            codigoMunicipio TEXT,
            idMunicipioDpto INTEGER,
            FOREIGN KEY (idMunicipioDpto) REFERENCES DimensionDepartamento(idDepartamento)
        )
        ''')

        # Tabla de Hechos
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS TablaHechosSNIES (
            idHecho INTEGER PRIMARY KEY,
            idTiempo INTEGER,
            idEstudiante INTEGER,
            idAcademico INTEGER,
            idInstitucion INTEGER,
            inscritos INTEGER,
            admitidos INTEGER,
            matriculados INTEGER,
            graduados INTEGER,
            FOREIGN KEY (idTiempo) REFERENCES DimensionTemporal(idTiempo),
            FOREIGN KEY (idEstudiante) REFERENCES DimensionEstudiantes(idEstudiante),
            FOREIGN KEY (idAcademico) REFERENCES DimensionAcademica(idAcademico),
            FOREIGN KEY (idInstitucion) REFERENCES DimensionInstitucion(idInstitucion)
        )
        ''')

        print("Tablas creadas exitosamente en SQLite.")
        self.close()
    
    def insert_dimension_data(self, cursor, table_name, data):
        """
        Inserta datos en una tabla dimensional y retorna el ID generado.
        """
        placeholders = ','.join(['?' for _ in data])
        columns = ','.join(data.keys())
        query = f"INSERT OR IGNORE INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, list(data.values()))
    
        # Obtener el ID insertado o existente
        where_clause = ' AND '.join([f"{k}=?" for k in data.keys()])
        cursor.execute(f"SELECT rowid FROM {table_name} WHERE {where_clause}", list(data.values()))
        return cursor.fetchone()[0]

    def process_dataframe_to_db(self, df):
        """
        Procesa un DataFrame y lo inserta en la base de datos.
        """
        self.connect()
        for _, row in df.iterrows():
            # Insertar en las tablas dimensionales
            
            departamento_data = {
                'nombreDepartamento': row['DEPARTAMENTO DE OFERTA DEL PROGRAMA'],
                'codigoDepartamento': row['CÓDIGO DEL DEPARTAMENTO (PROGRAMA)']
            }
            id_departamento = self.insert_dimension_data(self.cursor, 'DimensionDepartamento', departamento_data)
            
            institucion_data = {
                'nombreInstitucion': row['INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)'],
                'tipoInstitucion': row['CARÁCTER IES'],
                'idInstitucionDpto': id_departamento
            }
            id_institucion = self.insert_dimension_data(self.cursor, 'DimensionInstitucion', institucion_data)

            municipio_data = {
                'nombreMunicipio': row['MUNICIPIO DE OFERTA DEL PROGRAMA'],
                'codigoMunicipio': row['CÓDIGO DEL MUNICIPIO (PROGRAMA)'],
                'idMunicipioDpto': id_departamento
            }
            id_municipio = self.insert_dimension_data(self.cursor, 'DimensionMunicipio', municipio_data)

            tiempo_data = {
                'anio': row['AÑO'],
                'semestre': row['SEMESTRE']
            }
            id_tiempo = self.insert_dimension_data(self.cursor, 'DimensionTemporal', tiempo_data)

            estudiante_data = {'Genero': row['SEXO']}
            id_estudiante = self.insert_dimension_data(self.cursor, 'DimensionEstudiantes', estudiante_data)

            academica_data = {
                'nivelEducativo': row['NIVEL ACADÉMICO'],
                'programaAcademico': row['PROGRAMA ACADÉMICO'],
                'modalidad': row['MODALIDAD']
            }
            id_academico = self.insert_dimension_data(self.cursor, 'DimensionAcademica', academica_data)

            # Insertar en la tabla de hechos
            hechos_data = {
                'idTiempo': id_tiempo,
                'idEstudiante': id_estudiante,
                'idAcademico': id_academico,
                'idInstitucion': id_institucion,
                'inscritos': row.get('INSCRITOS', 0),
                'admitidos': row.get('ADMITIDOS', 0),
                'matriculados': row.get('MATRICULADOS', 0),
                'graduados': row.get('GRADUADOS', 0)
            }
            placeholders = ','.join(['?' for _ in hechos_data])
            columns = ','.join(hechos_data.keys())
            query = f"INSERT INTO TablaHechosSNIES ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, list(hechos_data.values()))
        self.close()

class Cargue:
    def cargue_archivo(self, nombre_archivo, hoja, encabezado, codigo_institucion, dataset):
        df = pd.read_excel(nombre_archivo, sheet_name=hoja, header=encabezado, dtype={'CÓDIGO DEL DEPARTAMENTO (PROGRAMA)': str})

        # Definir las columnas necesarias según el dataset
        if dataset == 'A':
            df = df[columnas_requeridas_A]
        elif dataset == 'M':
            df = df[columnas_requeridas_M]
        elif dataset == 'G':
            df = df[columnas_requeridas_G]
        elif dataset == 'I':
            df = df[columnas_requeridas_I]

        # Filtrar por código de institución
        # df = df[df['CÓDIGO DE LA INSTITUCIÓN'] == codigo_institucion]
        df = df[df["INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)"].isin(codigo_institucion)]
        
        return df
    
    def unificar_dataframes(self, df_inscritos, df_matriculados, df_admitidos, df_graduados):
        """
        Unifica los DataFrames usando las columnas comunes y mantiene las métricas específicas de cada uno.
        """
        columnas_merge = [
            'CÓDIGO DE LA INSTITUCIÓN',
            'INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)',
            'CARÁCTER IES',
            'PROGRAMA ACADÉMICO',
            'NIVEL ACADÉMICO',
            'MODALIDAD',
            'CÓDIGO DEL DEPARTAMENTO (PROGRAMA)',
            'DEPARTAMENTO DE OFERTA DEL PROGRAMA',
            'CÓDIGO DEL MUNICIPIO (PROGRAMA)',
            'MUNICIPIO DE OFERTA DEL PROGRAMA',
            'SEXO',
            'AÑO',
            'SEMESTRE'
        ]

        df_final = df_inscritos[columnas_merge + ['INSCRITOS']].copy()
        if df_matriculados is not None:
            df_final = df_final.merge(df_matriculados[columnas_merge + ['MATRICULADOS']], on=columnas_merge, how='outer')
        if df_admitidos is not None:
            df_final = df_final.merge(df_admitidos[columnas_merge + ['ADMITIDOS']], on=columnas_merge, how='outer')
        if df_graduados is not None:
            df_final = df_final.merge(df_graduados[columnas_merge + ['GRADUADOS']], on=columnas_merge, how='outer')

        metricas = ['INSCRITOS', 'MATRICULADOS', 'ADMITIDOS', 'GRADUADOS']
        df_final[metricas] = df_final[metricas].fillna(0)

        return df_final

# Hecho por:
# Óscar Julian Ramirez Contreras
# Santiago Jair Torres Rivera