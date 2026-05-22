import pandas as pd
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH  = BASE_DIR / "datos" / "dataset_asistencia_it 26A.csv"
OUTPUT_PATH = BASE_DIR / "informes" / "dataset_limpio_enriquecido.csv"
DIAS_LABORABLES = 22
UMBRAL_MINIMO   = 60.0

print("=" * 65)
print("  ANÁLISIS DE ASISTENCIA IT ")
print("=" * 65)

# ─── 1. CARGA DE DATOS ────────────────────────────────────────────────────────
print("\n[1/8] Cargando dataset...")
df = pd.read_csv(INPUT_PATH)
print(f"      ✓ {len(df)} registros cargados | {df.shape[1]} columnas")
print(f"      Columnas: {list(df.columns)}")

# ─── 2. AUDITORÍA DE CALIDAD ──────────────────────────────────────────────────
print("\n[2/8] Auditoría de calidad de datos...")
nulos = df.isnull().sum()
if nulos.sum() == 0:
    print("      ✓ Sin valores nulos detectados")
else:
    print(f"      ⚠ Valores nulos encontrados:\n{nulos[nulos > 0]}")

duplicados = df.duplicated('ID_Empleado').sum()
print(f"      ✓ Duplicados de ID: {duplicados}")

print(f"      ✓ Rango Dias_Asistidos: {df['Dias_Asistidos'].min()} – {df['Dias_Asistidos'].max()}")
print(f"      ✓ Días laborables fijos: {df['Dias_Laborables_Mes'].unique()} → OK")

# ─── 3. KPI PRINCIPAL: % ASISTENCIA ──────────────────────────────────────────
print("\n[3/8] Calculando KPI principal: % Asistencia Presencial...")
df['Pct_Asistencia'] = (df['Dias_Asistidos'] / df['Dias_Laborables_Mes'] * 100).round(2)
print(f"      ✓ Asistencia promedio global: {df['Pct_Asistencia'].mean():.2f}%")
print(f"      ✓ Rango: {df['Pct_Asistencia'].min()}% – {df['Pct_Asistencia'].max()}%")

# ─── 4. CLASIFICACIÓN DE CUMPLIMIENTO ────────────────────────────────────────
print(f"\n[4/8] Clasificando cumplimiento (umbral: {UMBRAL_MINIMO}%)...")
df['Cumple_Minimo'] = df['Pct_Asistencia'] >= UMBRAL_MINIMO

cumple    = df['Cumple_Minimo'].sum()
no_cumple = len(df) - cumple
print(f"      ✓ Cumplen  (≥60%): {cumple:>3} colaboradores ({cumple/len(df)*100:.1f}%)")
print(f"      ⚠ En riesgo (<60%): {no_cumple:>3} colaboradores ({no_cumple/len(df)*100:.1f}%)")

# ─── 5. DÍAS EFECTIVOS Y MODALIDAD ───────────────────────────────────────────
print("\n[5/8] Calculando días efectivos (presencial + remoto)...")
df['Dias_Efectivos']  = df['Dias_Asistidos'] + df['Dias_Remotos']
df['Pct_Efectivo']    = (df['Dias_Efectivos'] / df['Dias_Laborables_Mes'] * 100).round(2)
df['Modalidad_Remote']= df['Dias_Remotos'].apply(
    lambda x: 'Alta' if x >= 4 else ('Media' if x >= 2 else 'Baja')
)
print(f"      ✓ Efectividad promedio (pres+remoto): {df['Pct_Efectivo'].mean():.2f}%")

# ─── 6. MATRIZ DE RIESGO ─────────────────────────────────────────────────────
print("\n[6/8] Clasificando niveles de riesgo...")
def nivel_riesgo(pct):
    if pct >= 80:   return '🟢 Óptimo'
    elif pct >= 60: return '🔵 Aceptable'
    elif pct >= 45: return '🟡 En Riesgo'
    else:           return '🔴 Crítico'

df['Nivel_Riesgo'] = df['Pct_Asistencia'].apply(nivel_riesgo)

riesgo_dist = df['Nivel_Riesgo'].value_counts()
for nivel, count in riesgo_dist.items():
    print(f"      {nivel}: {count} colaboradores")

# ─── 7. ANÁLISIS POR ÁREA (KPI #5) ───────────────────────────────────────────
print("\n[7/8] KPIs por Área...")
kpis_area = df.groupby('Area').agg(
    Total_Empleados    = ('ID_Empleado', 'count'),
    Asistencia_Prom    = ('Pct_Asistencia', 'mean'),
    En_Riesgo          = ('Cumple_Minimo', lambda x: (~x).sum()),
    Dias_Remotos_Prom  = ('Dias_Remotos', 'mean'),
    Vac_Acum_Prom      = ('Vacaciones_Disponibles', 'mean'),
    Pct_Efectivo_Prom  = ('Pct_Efectivo', 'mean'),
).round(2).reset_index()
kpis_area['Tasa_Riesgo_%'] = (kpis_area['En_Riesgo'] / kpis_area['Total_Empleados'] * 100).round(1)

print(kpis_area.to_string(index=False))

# ─── 8. REPORTE FINAL DE KPIs ────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  REPORTE DE KPIs")
print("=" * 65)

kpis = {
    "KPI 1 — Total Colaboradores"                : f"{len(df)}",
    "KPI 2 — Cumplen Mínimo 60%"                 : f"{cumple} ({cumple/len(df)*100:.1f}%)",
    "KPI 3 — En Riesgo (<60%)"                   : f"{no_cumple} ({no_cumple/len(df)*100:.1f}%)",
    "KPI 4 — Asistencia Presencial Promedio"      : f"{df['Pct_Asistencia'].mean():.2f}%",
    "KPI 5 — Área con más casos en riesgo"        : kpis_area.loc[kpis_area['En_Riesgo'].idxmax(), 'Area'],
    "KPI 6 — Vacaciones por vencer (>10 días)"    : f"{(df['Vacaciones_Disponibles'] > 10).sum()} colaboradores",
    "KPI 7 — Días remotos promedio / mes"         : f"{df['Dias_Remotos'].mean():.2f} días",
    "KPI 8 — Colaboradores en nivel crítico (<45%)": f"{(df['Pct_Asistencia'] < 45).sum()}",
}

for k, v in kpis.items():
    print(f"  {k:<45} → {v}")

# ─── COLABORADORES EN RIESGO (detalle) ───────────────────────────────────────
print("\n" + "-" * 65)
print("  COLABORADORES EN RIESGO — TOP 15 MÁS CRÍTICOS")
print("-" * 65)
en_riesgo = df[~df['Cumple_Minimo']].sort_values('Pct_Asistencia')[
    ['Nombre', 'Area', 'Pct_Asistencia', 'Nivel_Riesgo', 'Estatus', 'Vacaciones_Disponibles']
].head(15)
print(en_riesgo.to_string(index=False))

# ─── EXPORTAR ─────────────────────────────────────────────────────────────────
print(f"\n[8/8] Exportando dataset limpio enriquecido...")
cols_export = [
    'ID_Empleado', 'Nombre', 'Area', 'Estatus',
    'Dias_Laborables_Mes', 'Dias_Asistidos', 'Dias_Remotos',
    'Dias_Permiso', 'Dias_Efectivos', 'Vacaciones_Disponibles',
    'Pct_Asistencia', 'Pct_Efectivo', 'Cumple_Minimo',
    'Nivel_Riesgo', 'Modalidad_Remote', 'Fecha_Expiracion_Vacaciones'
]
df[cols_export].to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"      ✓ Guardado en: {OUTPUT_PATH}")
print(f"      ✓ {len(df)} registros | {len(cols_export)} columnas")
print("\n✅ Análisis completo. ")
print("=" * 65)