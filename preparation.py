from model import Database, Cargue

# Crear instancia de la base de datos y las tablas
db = Database('snies.db')
db.create_tables()

# Cargar los datos
carga = Cargue()
institucion = 2712

# Cargar los DataFrames individuales
df_admitidos = carga.cargue_archivo(nombre_archivo='ADM-2023.xlsx', hoja=1, encabezado=5, 
                                    codigo_institucion=institucion, dataset='A')
df_matriculados = carga.cargue_archivo(nombre_archivo='MAT-2023.xlsx', hoja=1, encabezado=5, 
                                       codigo_institucion=institucion, dataset='M')
df_graduados = carga.cargue_archivo(nombre_archivo='GRA-2023.xlsx', hoja=1, encabezado=5, 
                                    codigo_institucion=institucion, dataset='G')
df_inscritos = carga.cargue_archivo(nombre_archivo='INS-2023.xlsx', hoja=1, encabezado=5, 
                                    codigo_institucion=institucion, dataset='I')

# Unificar los DataFrames
df_unificado = carga.unificar_dataframes(df_inscritos, df_matriculados, df_admitidos, df_graduados)

# Procesar el DataFrame unificado para la base de datos
db.process_dataframe_to_db(df_unificado)
