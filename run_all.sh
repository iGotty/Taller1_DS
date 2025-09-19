#!/bin/bash

# Script para ejecutar el análisis completo de reservas hoteleras
# Autor: Equipo de Data Science
# Fecha: 2024

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_status() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# Banner inicial
echo "================================================"
echo "   ANÁLISIS DE CANCELACIONES HOTELERAS"
echo "   Taller 1 - Data Science"
echo "================================================"
echo ""

# Verificar Python
print_status "Verificando instalación de Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
print_status "Python $PYTHON_VERSION detectado"

# Verificar si existe ambiente virtual
if [ -d "venv" ]; then
    print_status "Activando ambiente virtual..."
    source venv/bin/activate
else
    print_warning "No se encontró ambiente virtual"
    read -p "¿Desea crear uno? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Creando ambiente virtual..."
        python3 -m venv venv
        source venv/bin/activate
    fi
fi

# Instalar dependencias
print_status "Instalando dependencias..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    print_status "Dependencias instaladas correctamente"
else
    print_error "Error al instalar dependencias"
    exit 1
fi

# Crear directorios necesarios
print_status "Creando estructura de directorios..."
mkdir -p reports/figures
mkdir -p data

# Verificar que existan los datos
if [ ! -f "data/hotel_bookings_modified.csv" ]; then
    print_error "No se encuentra el archivo de datos: data/hotel_bookings_modified.csv"
    exit 1
fi

# Ejecutar notebooks en orden
print_status "Iniciando análisis de datos..."
echo ""

# Notebook 1: Entendimiento de datos
print_status "[1/4] Ejecutando análisis exploratorio..."
jupyter nbconvert --to notebook --execute notebooks/01_entendimiento_datos.ipynb \
    --ExecutePreprocessor.timeout=600 \
    --output 01_entendimiento_datos.ipynb 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "✓ Análisis exploratorio completado"
else
    print_error "Error en análisis exploratorio"
    exit 1
fi

# Notebook 2: Estrategia de análisis
print_status "[2/4] Definiendo estrategia analítica..."
jupyter nbconvert --to notebook --execute notebooks/02_estrategia_analisis.ipynb \
    --ExecutePreprocessor.timeout=600 \
    --output 02_estrategia_analisis.ipynb 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "✓ Estrategia definida"
else
    print_error "Error al definir estrategia"
    exit 1
fi

# Notebook 3: Desarrollo de estrategia
print_status "[3/4] Ejecutando análisis completo y modelado..."
jupyter nbconvert --to notebook --execute notebooks/03_desarrollo_estrategia.ipynb \
    --ExecutePreprocessor.timeout=1200 \
    --output 03_desarrollo_estrategia.ipynb 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "✓ Análisis y modelado completados"
else
    print_error "Error en análisis y modelado"
    exit 1
fi

# Notebook 4: Informe ejecutivo
print_status "[4/4] Generando informe ejecutivo..."
jupyter nbconvert --to notebook --execute notebooks/04_informe_ejecutivo.ipynb \
    --ExecutePreprocessor.timeout=600 \
    --output 04_informe_ejecutivo.ipynb 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "✓ Informe ejecutivo generado"
else
    print_error "Error al generar informe"
    exit 1
fi

# Generar presentación
print_status "Generando presentación PowerPoint..."
python3 src/generate_presentation.py
if [ $? -eq 0 ]; then
    print_status "✓ Presentación generada"
else
    print_error "Error al generar presentación"
    exit 1
fi

# Resumen final
echo ""
echo "================================================"
echo -e "${GREEN}   ANÁLISIS COMPLETADO EXITOSAMENTE${NC}"
echo "================================================"
echo ""
print_status "Resultados disponibles en:"
echo "  📊 Notebooks ejecutados: notebooks/"
echo "  📈 Visualizaciones: reports/figures/"
echo "  📑 Presentación: reports/presentacion_taller.pptx"
echo "  📝 Resúmenes: reports/*.txt"
echo ""

# Mostrar estadísticas básicas
if [ -f "reports/03_desarrollo_resultados.txt" ]; then
    echo "Métricas clave del análisis:"
    echo "----------------------------"
    grep -E "Tasa de cancelación|ROI|Recuperación" reports/03_desarrollo_resultados.txt | head -3
fi

echo ""
print_status "Tiempo total de ejecución: $SECONDS segundos"