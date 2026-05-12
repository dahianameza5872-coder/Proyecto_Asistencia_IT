import pandas as pd
import os

# Rutas relativas (funciona desde cualquier lugar)
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'datos', 'dataset_asistencia_it 26A.csv')
df = pd.read_csv(data_path)

# Agregar columna de % Asistencia
df['Dias_Laborables_Mes'] = 22
df['% Asistencia'] = (df['Dias_Asistidos'] / df['Dias_Laborables_Mes']) * 100

# 1. Empleados por debajo del 60%
riesgo = df[df['% Asistencia'] < 60]
print(f"Empleados en riesgo (<60%): {len(riesgo)}")
print(riesgo[['Nombre', 'Area', '% Asistencia', 'Dias_Permiso']])

# 2. Áreas con más casos bajos
area_riesgo = df.groupby('Area').apply(
    lambda x: (x['% Asistencia'] < 60).sum()
).sort_values(ascending=False)
print("Áreas con más empleados en riesgo:\n", area_riesgo)

# 3. Relación permisos vs asistencia (correlación)
correlacion = df['Dias_Permiso'].corr(df['% Asistencia'])
print(f"Correlación permisos vs asistencia: {correlacion:.2f}")

# Guardar resultados en Excel (en informes)
output_excel = os.path.join(script_dir, '..', 'informes', 'analisis_inicial.xlsx')
with pd.ExcelWriter(output_excel) as writer:
    df.to_excel(writer, sheet_name='Datos_Completos', index=False)
    riesgo.to_excel(writer, sheet_name='Empleados_Riesgo', index=False)
print(f"Archivo guardado: {output_excel}")