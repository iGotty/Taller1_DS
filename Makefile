.PHONY: help setup run clean figures presentation all

# Variables
PYTHON := python3
PIP := pip3
NOTEBOOKS_DIR := notebooks
REPORTS_DIR := reports
FIGURES_DIR := reports/figures
SRC_DIR := src

# Colores para output
GREEN := \033[0;32m
NC := \033[0m # No Color

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Instala dependencias del proyecto
	@echo "$(GREEN)Instalando dependencias...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Creando directorios necesarios...$(NC)"
	@mkdir -p $(FIGURES_DIR)
	@echo "$(GREEN)Setup completado!$(NC)"

run: ## Ejecuta todos los notebooks en orden
	@echo "$(GREEN)Ejecutando análisis completo...$(NC)"
	@echo "$(GREEN)[1/5] Entendimiento de datos...$(NC)"
	$(PYTHON) -m jupyter nbconvert --to notebook --execute $(NOTEBOOKS_DIR)/01_entendimiento_datos.ipynb --output 01_entendimiento_datos.ipynb
	@echo "$(GREEN)[2/5] Estrategia de análisis...$(NC)"
	$(PYTHON) -m jupyter nbconvert --to notebook --execute $(NOTEBOOKS_DIR)/02_estrategia_analisis.ipynb --output 02_estrategia_analisis.ipynb
	@echo "$(GREEN)[3/5] Desarrollo de estrategia...$(NC)"
	$(PYTHON) -m jupyter nbconvert --to notebook --execute $(NOTEBOOKS_DIR)/03_desarrollo_estrategia.ipynb --output 03_desarrollo_estrategia.ipynb
	@echo "$(GREEN)[4/5] Informe ejecutivo...$(NC)"
	$(PYTHON) -m jupyter nbconvert --to notebook --execute $(NOTEBOOKS_DIR)/04_informe_ejecutivo.ipynb --output 04_informe_ejecutivo.ipynb
	@echo "$(GREEN)[5/5] Generando presentación...$(NC)"
	$(PYTHON) $(SRC_DIR)/generate_presentation.py
	@echo "$(GREEN)Análisis completado exitosamente!$(NC)"

figures: ## Genera solo las figuras
	@echo "$(GREEN)Generando visualizaciones...$(NC)"
	$(PYTHON) -m jupyter nbconvert --to notebook --execute $(NOTEBOOKS_DIR)/01_entendimiento_datos.ipynb --output temp.ipynb
	$(PYTHON) -m jupyter nbconvert --to notebook --execute $(NOTEBOOKS_DIR)/03_desarrollo_estrategia.ipynb --output temp.ipynb
	@rm -f $(NOTEBOOKS_DIR)/temp.ipynb
	@echo "$(GREEN)Figuras generadas en $(FIGURES_DIR)$(NC)"

presentation: ## Genera solo la presentación
	@echo "$(GREEN)Generando presentación PowerPoint...$(NC)"
	$(PYTHON) $(SRC_DIR)/generate_presentation.py
	@echo "$(GREEN)Presentación generada en $(REPORTS_DIR)/presentacion_taller.pptx$(NC)"

clean: ## Limpia archivos temporales y outputs
	@echo "$(GREEN)Limpiando archivos temporales...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
	@rm -f $(NOTEBOOKS_DIR)/*.nbconvert.ipynb
	@echo "$(GREEN)Limpieza completada!$(NC)"

test: ## Valida que los notebooks se ejecuten sin errores
	@echo "$(GREEN)Validando notebooks...$(NC)"
	@for nb in $(NOTEBOOKS_DIR)/*.ipynb; do \
		echo "Testeando $$nb..."; \
		$(PYTHON) -m jupyter nbconvert --to notebook --execute $$nb --stdout > /dev/null || exit 1; \
	done
	@echo "$(GREEN)Todos los notebooks se ejecutan correctamente!$(NC)"

all: clean setup run ## Ejecuta todo el pipeline completo
	@echo "$(GREEN)Pipeline completo ejecutado exitosamente!$(NC)"
	@echo "$(GREEN)Resultados disponibles en:$(NC)"
	@echo "  - Notebooks ejecutados: $(NOTEBOOKS_DIR)/"
	@echo "  - Figuras: $(FIGURES_DIR)/"
	@echo "  - Presentación: $(REPORTS_DIR)/presentacion_taller.pptx"
	@echo "  - Resúmenes: $(REPORTS_DIR)/*.txt"