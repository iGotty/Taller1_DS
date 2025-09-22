# Análisis de Demanda y Ocupación Hotelera

## Objetivo
Análisis integral de datos de reservas hoteleras para identificar patrones de demanda, factores de cancelación y oportunidades de optimización de ocupación en hoteles de ciudad y resort.

## Integrantes
-Juan Esteban Cuellar Argotty 202014258
-Juan David Valencia Camargo 2017288857

## Estructura del Proyecto

```
├── data/                      # Datos fuente
│   ├── hotel_bookings_modified.csv
│   └── Hotel Bookings Demand Data Dictionary.xlsx
├── notebooks/                 # Análisis en notebooks
│   ├── 01_entendimiento_datos.ipynb
│   ├── 02_estrategia_analisis.ipynb
│   ├── 03_desarrollo_estrategia.ipynb
│   └── 04_informe_ejecutivo.ipynb
├── reports/                   # Reportes y visualizaciones
│   ├── Análisis de cancelaciones y ocupación hotelera.pdf              # presentacion final
│   ├── figures/              # Gráficos exportados
│   └── presentacion_taller.pptx
├── src/                      # Código fuente reutilizable
│   ├── utils_io.py          # Funciones de carga de datos
│   ├── utils_viz.py         # Funciones de visualización
│   └── utils_stats.py       # Funciones estadísticas
└── Makefile                  # Automatización de tareas
```

## Instalación y Ejecución

### Requisitos
- Python 3.11+
- Sistema operativo: Linux/macOS/Windows

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### Ejecución Completa
```bash
make run  # Ejecuta todos los notebooks en orden
```

### Ejecución Individual
Los notebooks deben ejecutarse en orden numérico:
1. `jupyter notebook notebooks/01_entendimiento_datos.ipynb`
2. `jupyter notebook notebooks/02_estrategia_analisis.ipynb`
3. `jupyter notebook notebooks/03_desarrollo_estrategia.ipynb`
4. `jupyter notebook notebooks/04_informe_ejecutivo.ipynb`

## Insights Clave

### Patrones de Cancelación
- **Lead Time**: Mayor anticipación correlaciona con mayor tasa de cancelación
- **Tipo de Hotel**: Diferencias significativas entre City Hotel y Resort Hotel
- **Depósitos**: Impacto directo del tipo de depósito en la probabilidad de cancelación

### Factores de Ocupación
- **Estacionalidad**: Patrones claros por temporada alta/baja
- **Composición de Huéspedes**: Familias vs. viajeros individuales
- **Canal de Distribución**: Variabilidad por canal de reserva

## Recomendaciones Principales

1. **Política de Depósitos Diferenciada**: Implementar depósitos no reembolsables para reservas con lead time > 60 días
2. **Overbooking Inteligente**: Ajustar niveles por temporada y tipo de hotel basado en tasas históricas
3. **Pricing Dinámico**: Ajustar ADR según ventana de reserva y probabilidad de cancelación
4. **Segmentación de Canales**: Optimizar asignación de inventario por canal según performance

## Metodología

- **Limpieza de Datos**: Tratamiento de valores faltantes y outliers
- **Ingeniería de Variables**: Creación de features relevantes (total_guests, total_stay_nights, etc.)
- **Análisis Estadístico**: Tests de hipótesis y análisis multivariante
- **Modelado Predictivo**: Modelo interpretable de probabilidad de cancelación

## Limitaciones

- Datos históricos sin información de competencia
- No incluye factores externos (eventos, clima, economía)
- Sesgo temporal en patrones pre/post pandemia
