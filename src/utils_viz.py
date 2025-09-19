"""
Utilidades para visualización de datos
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Tuple, Optional, List
import warnings
warnings.filterwarnings('ignore')

# Configuración global de estilo
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
sns.set_style("whitegrid")
sns.set_palette("husl")

def setup_plot_style():
    """Configura el estilo global de visualización."""
    sns.set_style("whitegrid")
    sns.set_context("notebook", font_scale=1.1)
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 300

def plot_univariate_analysis(df: pd.DataFrame, column: str, figsize: Tuple[int, int] = (12, 4)) -> plt.Figure:
    """
    Genera análisis univariado con histograma y boxplot.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
    column : str
        Columna a analizar
    figsize : tuple
        Tamaño de la figura
        
    Returns
    -------
    plt.Figure
        Figura con los gráficos
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    
    # Verificar tipo de variable
    if df[column].dtype in ['object', 'category']:
        # Variable categórica
        # Gráfico de barras
        value_counts = df[column].value_counts()
        axes[0].bar(range(len(value_counts)), value_counts.values)
        axes[0].set_xticks(range(len(value_counts)))
        axes[0].set_xticklabels(value_counts.index, rotation=45, ha='right')
        axes[0].set_title(f'Distribución de {column}')
        axes[0].set_ylabel('Frecuencia')
        
        # Gráfico de pastel si hay pocas categorías
        if len(value_counts) <= 8:
            axes[1].pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
            axes[1].set_title(f'Proporción de {column}')
        else:
            axes[1].text(0.5, 0.5, 'Demasiadas categorías\npara gráfico de pastel', 
                        ha='center', va='center', fontsize=12)
            axes[1].set_xlim(0, 1)
            axes[1].set_ylim(0, 1)
        
        # Tabla de frecuencias
        axes[2].axis('tight')
        axes[2].axis('off')
        table_data = pd.DataFrame({
            'Categoría': value_counts.index[:10],
            'Frecuencia': value_counts.values[:10],
            'Porcentaje': (value_counts.values[:10] / len(df) * 100).round(2)
        })
        table = axes[2].table(cellText=table_data.values,
                             colLabels=table_data.columns,
                             cellLoc='center',
                             loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        axes[2].set_title(f'Top 10 categorías de {column}')
        
    else:
        # Variable numérica
        data_clean = df[column].dropna()
        
        # Histograma
        axes[0].hist(data_clean, bins=30, edgecolor='black', alpha=0.7)
        axes[0].set_title(f'Histograma de {column}')
        axes[0].set_xlabel(column)
        axes[0].set_ylabel('Frecuencia')
        axes[0].axvline(data_clean.mean(), color='red', linestyle='--', label=f'Media: {data_clean.mean():.2f}')
        axes[0].axvline(data_clean.median(), color='green', linestyle='--', label=f'Mediana: {data_clean.median():.2f}')
        axes[0].legend()
        
        # Boxplot
        axes[1].boxplot(data_clean, vert=True)
        axes[1].set_title(f'Boxplot de {column}')
        axes[1].set_ylabel(column)
        
        # Estadísticas
        stats_text = f"""
        Media: {data_clean.mean():.2f}
        Mediana: {data_clean.median():.2f}
        Desv. Est.: {data_clean.std():.2f}
        Min: {data_clean.min():.2f}
        Max: {data_clean.max():.2f}
        Q1: {data_clean.quantile(0.25):.2f}
        Q3: {data_clean.quantile(0.75):.2f}
        IQR: {data_clean.quantile(0.75) - data_clean.quantile(0.25):.2f}
        Asimetría: {data_clean.skew():.2f}
        Curtosis: {data_clean.kurtosis():.2f}
        """
        axes[2].text(0.1, 0.5, stats_text, fontsize=10, va='center')
        axes[2].set_xlim(0, 1)
        axes[2].set_ylim(0, 1)
        axes[2].axis('off')
        axes[2].set_title(f'Estadísticas de {column}')
    
    plt.tight_layout()
    return fig

def plot_cancellation_analysis(df: pd.DataFrame, group_by: str, figsize: Tuple[int, int] = (12, 5)) -> plt.Figure:
    """
    Analiza tasas de cancelación por categoría.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
    group_by : str
        Variable por la cual agrupar
    figsize : tuple
        Tamaño de la figura
        
    Returns
    -------
    plt.Figure
        Figura con el análisis
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    # Calcular tasas de cancelación
    cancel_rates = df.groupby(group_by)['is_canceled'].agg(['mean', 'sum', 'count'])
    cancel_rates.columns = ['tasa_cancelacion', 'total_cancelaciones', 'total_reservas']
    cancel_rates = cancel_rates.sort_values('tasa_cancelacion', ascending=False)
    
    # Gráfico de barras de tasas
    axes[0].bar(range(len(cancel_rates)), cancel_rates['tasa_cancelacion'] * 100)
    axes[0].set_xticks(range(len(cancel_rates)))
    axes[0].set_xticklabels(cancel_rates.index, rotation=45, ha='right')
    axes[0].set_title(f'Tasa de Cancelación por {group_by}')
    axes[0].set_ylabel('Tasa de Cancelación (%)')
    axes[0].axhline(y=df['is_canceled'].mean() * 100, color='red', 
                   linestyle='--', label=f'Media global: {df["is_canceled"].mean()*100:.1f}%')
    axes[0].legend()
    
    # Gráfico de volumen
    axes[1].bar(range(len(cancel_rates)), cancel_rates['total_reservas'], 
               label='Total Reservas', alpha=0.7)
    axes[1].bar(range(len(cancel_rates)), cancel_rates['total_cancelaciones'], 
               label='Cancelaciones', alpha=0.7)
    axes[1].set_xticks(range(len(cancel_rates)))
    axes[1].set_xticklabels(cancel_rates.index, rotation=45, ha='right')
    axes[1].set_title(f'Volumen de Reservas por {group_by}')
    axes[1].set_ylabel('Cantidad')
    axes[1].legend()
    
    plt.tight_layout()
    return fig

def plot_bivariate_analysis(df: pd.DataFrame, x: str, y: str, hue: Optional[str] = None, 
                           figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Análisis bivariado entre dos variables.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
    x : str
        Variable eje X
    y : str
        Variable eje Y
    hue : str, optional
        Variable para color
    figsize : tuple
        Tamaño de la figura
        
    Returns
    -------
    plt.Figure
        Figura con el análisis
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Determinar tipo de gráfico según tipos de variables
    x_type = 'cat' if df[x].dtype in ['object', 'category'] or df[x].nunique() < 10 else 'num'
    y_type = 'cat' if df[y].dtype in ['object', 'category'] or df[y].nunique() < 10 else 'num'
    
    if x_type == 'num' and y_type == 'num':
        # Scatter plot para dos numéricas
        scatter = ax.scatter(df[x], df[y], alpha=0.5, c=df[hue] if hue else None)
        if hue:
            plt.colorbar(scatter, ax=ax, label=hue)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(f'{y} vs {x}')
        
    elif x_type == 'cat' and y_type == 'num':
        # Boxplot
        if hue:
            sns.boxplot(data=df, x=x, y=y, hue=hue, ax=ax)
        else:
            sns.boxplot(data=df, x=x, y=y, ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_title(f'Distribución de {y} por {x}')
        
    elif x_type == 'num' and y_type == 'cat':
        # Boxplot horizontal
        if hue:
            sns.boxplot(data=df, x=x, y=y, hue=hue, orient='h', ax=ax)
        else:
            sns.boxplot(data=df, x=x, y=y, orient='h', ax=ax)
        ax.set_title(f'Distribución de {x} por {y}')
        
    else:
        # Heatmap para dos categóricas
        crosstab = pd.crosstab(df[y], df[x], normalize='columns') * 100
        sns.heatmap(crosstab, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Porcentaje'})
        ax.set_title(f'Tabla Cruzada: {y} vs {x} (%)')
    
    plt.tight_layout()
    return fig

def plot_correlation_matrix(df: pd.DataFrame, figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
    """
    Matriz de correlación para variables numéricas.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
    figsize : tuple
        Tamaño de la figura
        
    Returns
    -------
    plt.Figure
        Figura con la matriz
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Seleccionar solo columnas numéricas
    numeric_cols = df.select_dtypes(include=['int', 'float']).columns
    corr_matrix = df[numeric_cols].corr()
    
    # Crear máscara para triángulo superior
    mask = np.triu(np.ones_like(corr_matrix), k=1)
    
    # Heatmap
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', 
                cmap='coolwarm', center=0, vmin=-1, vmax=1, 
                square=True, linewidths=1, ax=ax)
    ax.set_title('Matriz de Correlación')
    
    plt.tight_layout()
    return fig

def plot_time_series_analysis(df: pd.DataFrame, date_col: str, value_col: str, 
                             figsize: Tuple[int, int] = (14, 6)) -> plt.Figure:
    """
    Análisis de series temporales.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
    date_col : str
        Columna de fecha
    value_col : str
        Columna de valores
    figsize : tuple
        Tamaño de la figura
        
    Returns
    -------
    plt.Figure
        Figura con el análisis
    """
    fig, axes = plt.subplots(2, 1, figsize=figsize)
    
    # Preparar datos
    if date_col not in df.columns:
        # Crear fecha artificial si no existe
        df['fecha_artificial'] = pd.date_range(start='2015-01-01', periods=len(df), freq='D')
        date_col = 'fecha_artificial'
    
    ts_data = df.groupby(pd.Grouper(key=date_col, freq='M'))[value_col].agg(['mean', 'sum', 'count'])
    
    # Serie temporal
    axes[0].plot(ts_data.index, ts_data['mean'], marker='o', label='Media mensual')
    axes[0].fill_between(ts_data.index, ts_data['mean'] * 0.8, ts_data['mean'] * 1.2, alpha=0.2)
    axes[0].set_title(f'Evolución Temporal de {value_col}')
    axes[0].set_xlabel('Fecha')
    axes[0].set_ylabel(f'{value_col} (media)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Volumen
    axes[1].bar(ts_data.index, ts_data['count'], width=20, alpha=0.7)
    axes[1].set_title('Volumen de Registros por Mes')
    axes[1].set_xlabel('Fecha')
    axes[1].set_ylabel('Cantidad de Registros')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def save_figure(fig: plt.Figure, filename: str, path: str = "reports/figures/"):
    """
    Guarda una figura en el directorio especificado.
    
    Parameters
    ----------
    fig : plt.Figure
        Figura a guardar
    filename : str
        Nombre del archivo (sin extensión)
    path : str
        Directorio de destino
    """
    from pathlib import Path
    Path(path).mkdir(parents=True, exist_ok=True)
    
    # Guardar en múltiples formatos
    fig.savefig(f"{path}{filename}.png", dpi=300, bbox_inches='tight')
    fig.savefig(f"{path}{filename}.pdf", bbox_inches='tight')
    print(f"Figura guardada: {path}{filename}")