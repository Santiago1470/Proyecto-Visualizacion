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
            IdTiempo INTEGER PRIMARY KEY,
            Anio INTEGER,
            Semestre INTEGER
        )
        ''')

        # Dimensión Estudiantes
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionEstudiantes (
            IdEstudiante INTEGER PRIMARY KEY,
            Genero TEXT
        )
        ''')

        # Dimensión Académica
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionAcademica (
            IdAcademico INTEGER PRIMARY KEY,
            NivelEducativo TEXT,
            AreaConocimiento TEXT,
            Modalidad TEXT
        )
        ''')

        # Dimensión Institución
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionInstitucion (
            IdInstitucion INTEGER PRIMARY KEY,
            NombreInstitucion TEXT,
            TipoInstitucion TEXT
        )
        ''')

        # Dimensión Departamento
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionDepartamento (
            IdDepartamento INTEGER PRIMARY KEY,
            NombreDepartamento TEXT,
            CodigoDepartamento TEXT
        )
        ''')

        # Dimensión Municipio
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS DimensionMunicipio (
            IdMunicipio INTEGER PRIMARY KEY,
            NombreMunicipio TEXT,
            CodigoMunicipio TEXT,
            IdDepartamento INTEGER,
            FOREIGN KEY (IdDepartamento) REFERENCES DimensionDepartamento(IdDepartamento)
        )
        ''')

        # Tabla de Hechos
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS TablaHechosSNIES (
            IdHecho INTEGER PRIMARY KEY,
            IdTiempo INTEGER,
            IdEstudiante INTEGER,
            IdAcademico INTEGER,
            IdInstitucion INTEGER,
            IdDepartamento INTEGER,
            IdMunicipio INTEGER,
            CantidadInscritos INTEGER,
            CantidadAdmitidos INTEGER,
            CantidadMatriculados INTEGER,
            CantidadGraduados INTEGER,
            FOREIGN KEY (IdTiempo) REFERENCES DimensionTemporal(IdTiempo),
            FOREIGN KEY (IdEstudiante) REFERENCES DimensionEstudiantes(IdEstudiante),
            FOREIGN KEY (IdAcademico) REFERENCES DimensionAcademica(IdAcademico),
            FOREIGN KEY (IdInstitucion) REFERENCES DimensionInstitucion(IdInstitucion),
            FOREIGN KEY (IdDepartamento) REFERENCES DimensionDepartamento(IdDepartamento),
            FOREIGN KEY (IdMunicipio) REFERENCES DimensionMunicipio(IdMunicipio)
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
            institucion_data = {
                'NombreInstitucion': row['INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)'],
                'TipoInstitucion': row['CARÁCTER IES']
            }
            id_institucion = self.insert_dimension_data(self.cursor, 'DimensionInstitucion', institucion_data)

            tiempo_data = {
                'Anio': row['AÑO'],
                'Semestre': row['SEMESTRE']
            }
            id_tiempo = self.insert_dimension_data(self.cursor, 'DimensionTemporal', tiempo_data)

            estudiante_data = {'Genero': row['ID SEXO']}
            id_estudiante = self.insert_dimension_data(self.cursor, 'DimensionEstudiantes', estudiante_data)

            academica_data = {
                'NivelEducativo': row['NIVEL ACADÉMICO'],
                'AreaConocimiento': row['ÁREA DE CONOCIMIENTO'],
                'Modalidad': row['MODALIDAD']
            }
            id_academico = self.insert_dimension_data(self.cursor, 'DimensionAcademica', academica_data)

            # Insertar en la tabla de hechos
            hechos_data = {
                'IdTiempo': id_tiempo,
                'IdEstudiante': id_estudiante,
                'IdAcademico': id_academico,
                'IdInstitucion': id_institucion,
                'CantidadInscritos': row.get('INSCRITOS', 0),
                'CantidadAdmitidos': row.get('ADMITIDOS', 0),
                'CantidadMatriculados': row.get('MATRICULADOS', 0),
                'CantidadGraduados': row.get('GRADUADOS', 0)
            }
            placeholders = ','.join(['?' for _ in hechos_data])
            columns = ','.join(hechos_data.keys())
            query = f"INSERT INTO TablaHechosSNIES ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, list(hechos_data.values()))
        self.close()

class Cargue:
    def cargue_archivo(self, nombre_archivo, hoja, encabezado, codigo_institucion, dataset):
        df = pd.read_excel(nombre_archivo, sheet_name=hoja, header=encabezado)

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
        df = df[df['CÓDIGO DE LA INSTITUCIÓN'] == codigo_institucion]
        
        return df
    
    def unificar_dataframes(self, df_inscritos, df_matriculados, df_admitidos, df_graduados):
        """
        Unifica los DataFrames usando las columnas comunes y mantiene las métricas específicas de cada uno.
        """
        columnas_merge = [
            'CÓDIGO DE LA INSTITUCIÓN',
            'INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)',
            'CARÁCTER IES',
            'ÁREA DE CONOCIMIENTO',
            'NIVEL ACADÉMICO',
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
