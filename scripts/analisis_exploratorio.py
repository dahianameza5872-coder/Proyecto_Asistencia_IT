import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'datos', 'dataset_asistencia_it 26A.csv')
df = pd.read_csv(data_path)
df['% Asistencia'] = (df['Dias_Asistidos'] / 22) * 100

# Configurar estilo
sns.set_theme(style="whitegrid")
output_dir = os.path.join(script_dir, '..', 'informes')

# 1. Histograma
plt.figure(figsize=(10,6))
sns.histplot(df['% Asistencia'], bins=10, kde=True)
plt.axvline(60, color='red', linestyle='--', label='Umbral 60%')
plt.title('Distribución del % de Asistencia')
plt.legend()
plt.savefig(os.path.join(output_dir, 'histograma_asistencia.png'))
plt.close()

# 2. Boxplot por área
plt.figure(figsize=(12,6))
sns.boxplot(x='Area', y='% Asistencia', data=df)
plt.axhline(60, color='red', linestyle='--')
plt.title('Distribución de Asistencia por Área')
plt.xticks(rotation=45)
plt.savefig(os.path.join(output_dir, 'boxplot_area.png'))
plt.close()

# 3. Relación permisos vs asistencia
plt.figure(figsize=(8,6))
sns.scatterplot(x='Dias_Permiso', y='% Asistencia', hue='Estatus', data=df)
plt.title('Relación entre Días de Permiso y % Asistencia')
plt.savefig(os.path.join(output_dir, 'permisos_vs_asistencia.png'))
plt.close()

# 4. Resumen estadístico por área
resumen = df.groupby('Area')['% Asistencia'].agg(['mean', 'median', 'std', lambda x: (x<60).sum()])
resumen.columns = ['Promedio', 'Mediana', 'DesvEst', 'EnRiesgo']
resumen.to_csv(os.path.join(output_dir, 'resumen_area.csv'))
print("Gráficos y resumen guardados en", output_dir)