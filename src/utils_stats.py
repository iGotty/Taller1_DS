"""
Utilidades para análisis estadístico
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

def perform_chi_square_test(df: pd.DataFrame, var1: str, var2: str) -> Dict:
    """
    Realiza test chi-cuadrado entre dos variables categóricas.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
    var1 : str
        Primera variable categórica
    var2 : str
        Segunda variable categórica
        
    Returns
    -------
    dict
        Resultados del test
    """
    # Crear tabla de contingencia
    contingency_table = pd.crosstab(df[var1], df[var2])
    
    # Realizar test
    chi2, p_value, dof, expected_freq = stats.chi2_contingency(contingency_table)
    
    # Calcular Cramér's V
    n = contingency_table.sum().sum()
    min_dim = min(contingency_table.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
    
    # Interpretar resultado
    alpha = 0.05
    is_significant = p_value < alpha
    
    return {
        'chi2_statistic': chi2,
        'p_value': p_value,
        'degrees_of_freedom': dof,
        'cramers_v': cramers_v,
        'is_significant': is_significant,
        'interpretation': f"{'Existe' if is_significant else 'No existe'} asociación significativa entre {var1} y {var2} (p={p_value:.4f})",
        'effect_size': interpret_cramers_v(cramers_v),
        'contingency_table': contingency_table
    }

def interpret_cramers_v(v: float) -> str:
    """
    Interpreta el valor de Cramér's V.
    
    Parameters
    ----------
    v : float
        Valor de Cramér's V
        
    Returns
    -------
    str
        Interpretación del tamaño del efecto
    """
    if v < 0.1:
        return "Efecto despreciable"
    elif v < 0.3:
        return "Efecto pequeño"
    elif v < 0.5:
        return "Efecto mediano"
    else:
        return "Efecto grande"

def perform_t_test(df: pd.DataFrame, numeric_var: str, group_var: str, group1: str, group2: str) -> Dict:
    """
    Realiza t-test entre dos grupos.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
    numeric_var : str
        Variable numérica a comparar
    group_var : str
        Variable de agrupación
    group1 : str
        Primer grupo
    group2 : str
        Segundo grupo
        
    Returns
    -------
    dict
        Resultados del test
    """
    # Filtrar grupos
    data1 = df[df[group_var] == group1][numeric_var].dropna()
    data2 = df[df[group_var] == group2][numeric_var].dropna()
    
    # Verificar normalidad
    _, p_norm1 = stats.shapiro(data1) if len(data1) < 5000 else (None, 1)
    _, p_norm2 = stats.shapiro(data2) if len(data2) < 5000 else (None, 1)
    
    # Verificar homogeneidad de varianzas
    _, p_levene = stats.levene(data1, data2)
    
    # Decidir qué test usar
    if p_norm1 and p_norm2 and p_norm1 > 0.05 and p_norm2 > 0.05:
        # Datos normales, usar t-test
        if p_levene > 0.05:
            # Varianzas iguales
            t_stat, p_value = stats.ttest_ind(data1, data2, equal_var=True)
            test_type = "T-test (varianzas iguales)"
        else:
            # Varianzas diferentes (Welch)
            t_stat, p_value = stats.ttest_ind(data1, data2, equal_var=False)
            test_type = "T-test de Welch (varianzas diferentes)"
    else:
        # Datos no normales, usar Mann-Whitney
        u_stat, p_value = stats.mannwhitneyu(data1, data2, alternative='two-sided')
        t_stat = u_stat
        test_type = "Mann-Whitney U"
    
    # Calcular tamaño del efecto (Cohen's d)
    mean1, mean2 = data1.mean(), data2.mean()
    std1, std2 = data1.std(), data2.std()
    pooled_std = np.sqrt((std1**2 + std2**2) / 2)
    cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0
    
    # Interpretar resultado
    alpha = 0.05
    is_significant = p_value < alpha
    
    return {
        'test_type': test_type,
        'statistic': t_stat,
        'p_value': p_value,
        'mean_group1': mean1,
        'mean_group2': mean2,
        'std_group1': std1,
        'std_group2': std2,
        'cohens_d': cohens_d,
        'effect_size': interpret_cohens_d(abs(cohens_d)),
        'is_significant': is_significant,
        'interpretation': f"{'Existe' if is_significant else 'No existe'} diferencia significativa entre {group1} y {group2} (p={p_value:.4f})",
        'n_group1': len(data1),
        'n_group2': len(data2)
    }

def interpret_cohens_d(d: float) -> str:
    """
    Interpreta el valor de Cohen's d.
    
    Parameters
    ----------
    d : float
        Valor de Cohen's d
        
    Returns
    -------
    str
        Interpretación del tamaño del efecto
    """
    if d < 0.2:
        return "Efecto despreciable"
    elif d < 0.5:
        return "Efecto pequeño"
    elif d < 0.8:
        return "Efecto mediano"
    else:
        return "Efecto grande"

def perform_anova(df: pd.DataFrame, numeric_var: str, group_var: str) -> Dict:
    """
    Realiza ANOVA de un factor.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
    numeric_var : str
        Variable numérica dependiente
    group_var : str
        Variable categórica independiente
        
    Returns
    -------
    dict
        Resultados del ANOVA
    """
    # Preparar grupos
    groups = []
    group_names = []
    for name, group in df.groupby(group_var)[numeric_var]:
        groups.append(group.dropna())
        group_names.append(name)
    
    # Realizar ANOVA
    f_stat, p_value = stats.f_oneway(*groups)
    
    # Calcular eta-squared (tamaño del efecto)
    grand_mean = df[numeric_var].mean()
    ss_between = sum([len(g) * (g.mean() - grand_mean)**2 for g in groups])
    ss_total = sum([(x - grand_mean)**2 for g in groups for x in g])
    eta_squared = ss_between / ss_total if ss_total > 0 else 0
    
    # Interpretar resultado
    alpha = 0.05
    is_significant = p_value < alpha
    
    # Estadísticas descriptivas por grupo
    group_stats = pd.DataFrame({
        'group': group_names,
        'n': [len(g) for g in groups],
        'mean': [g.mean() for g in groups],
        'std': [g.std() for g in groups],
        'median': [g.median() for g in groups]
    })
    
    return {
        'f_statistic': f_stat,
        'p_value': p_value,
        'eta_squared': eta_squared,
        'effect_size': interpret_eta_squared(eta_squared),
        'is_significant': is_significant,
        'interpretation': f"{'Existe' if is_significant else 'No existe'} diferencia significativa entre grupos (p={p_value:.4f})",
        'group_stats': group_stats,
        'n_groups': len(groups)
    }

def interpret_eta_squared(eta2: float) -> str:
    """
    Interpreta el valor de eta-squared.
    
    Parameters
    ----------
    eta2 : float
        Valor de eta-squared
        
    Returns
    -------
    str
        Interpretación del tamaño del efecto
    """
    if eta2 < 0.01:
        return "Efecto despreciable"
    elif eta2 < 0.06:
        return "Efecto pequeño"
    elif eta2 < 0.14:
        return "Efecto mediano"
    else:
        return "Efecto grande"

def calculate_cancellation_metrics(df: pd.DataFrame, group_vars: List[str]) -> pd.DataFrame:
    """
    Calcula métricas de cancelación por grupos.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
    group_vars : list
        Variables por las cuales agrupar
        
    Returns
    -------
    pd.DataFrame
        DataFrame con métricas calculadas
    """
    metrics = df.groupby(group_vars).agg({
        'is_canceled': ['sum', 'mean', 'count']
    })
    
    metrics.columns = ['cancelaciones', 'tasa_cancelacion', 'total_reservas']
    metrics['no_canceladas'] = metrics['total_reservas'] - metrics['cancelaciones']
    metrics['tasa_confirmacion'] = 1 - metrics['tasa_cancelacion']
    
    # Agregar intervalos de confianza para la tasa
    metrics['ci_lower'] = metrics.apply(
        lambda row: calculate_proportion_ci(row['cancelaciones'], row['total_reservas'])[0], axis=1
    )
    metrics['ci_upper'] = metrics.apply(
        lambda row: calculate_proportion_ci(row['cancelaciones'], row['total_reservas'])[1], axis=1
    )
    
    # Ordenar por tasa de cancelación
    metrics = metrics.sort_values('tasa_cancelacion', ascending=False)
    
    return metrics

def calculate_proportion_ci(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calcula intervalo de confianza para una proporción.
    
    Parameters
    ----------
    successes : int
        Número de éxitos
    total : int
        Total de observaciones
    confidence : float
        Nivel de confianza
        
    Returns
    -------
    tuple
        (límite inferior, límite superior)
    """
    if total == 0:
        return (0, 0)
    
    p = successes / total
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    se = np.sqrt(p * (1 - p) / total)
    
    ci_lower = max(0, p - z * se)
    ci_upper = min(1, p + z * se)
    
    return (ci_lower, ci_upper)

def analyze_feature_importance(df: pd.DataFrame, target: str, features: List[str]) -> pd.DataFrame:
    """
    Analiza la importancia de variables para predecir el target.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
    target : str
        Variable objetivo
    features : list
        Lista de variables predictoras
        
    Returns
    -------
    pd.DataFrame
        DataFrame con importancia de variables
    """
    importance_scores = []
    
    for feature in features:
        if df[feature].dtype in ['object', 'category']:
            # Variable categórica - usar Cramér's V
            result = perform_chi_square_test(df, feature, target)
            score = result['cramers_v']
            test_type = 'Cramér\'s V'
        else:
            # Variable numérica - usar correlación punto-biserial
            score, p_value = stats.pointbiserialr(df[target], df[feature].fillna(df[feature].median()))
            score = abs(score)
            test_type = 'Correlación'
        
        importance_scores.append({
            'feature': feature,
            'importance_score': score,
            'test_type': test_type,
            'interpretation': interpret_importance_score(score)
        })
    
    importance_df = pd.DataFrame(importance_scores)
    importance_df = importance_df.sort_values('importance_score', ascending=False)
    
    return importance_df

def interpret_importance_score(score: float) -> str:
    """
    Interpreta un score de importancia.
    
    Parameters
    ----------
    score : float
        Score de importancia
        
    Returns
    -------
    str
        Interpretación
    """
    if score < 0.1:
        return "Muy baja"
    elif score < 0.3:
        return "Baja"
    elif score < 0.5:
        return "Moderada"
    elif score < 0.7:
        return "Alta"
    else:
        return "Muy alta"

def calculate_business_metrics(df: pd.DataFrame) -> Dict:
    """
    Calcula métricas de negocio relevantes.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con los datos
        
    Returns
    -------
    dict
        Métricas de negocio
    """
    metrics = {}
    
    # Métricas generales
    metrics['total_bookings'] = len(df)
    metrics['cancellation_rate'] = df['is_canceled'].mean()
    metrics['avg_lead_time'] = df['lead_time'].mean()
    metrics['avg_adr'] = df[df['adr'] > 0]['adr'].mean() if 'adr' in df.columns else 0
    
    # Métricas por tipo de hotel
    for hotel_type in df['hotel'].unique():
        hotel_data = df[df['hotel'] == hotel_type]
        metrics[f'{hotel_type}_cancellation_rate'] = hotel_data['is_canceled'].mean()
        metrics[f'{hotel_type}_avg_adr'] = hotel_data[hotel_data['adr'] > 0]['adr'].mean() if 'adr' in hotel_data.columns else 0
    
    # Pérdida potencial por cancelaciones
    if 'adr' in df.columns and 'total_stay_nights' in df.columns:
        canceled_bookings = df[df['is_canceled'] == 1]
        metrics['potential_revenue_loss'] = (canceled_bookings['adr'] * canceled_bookings['total_stay_nights']).sum()
    
    # Ocupación estimada
    total_room_nights = df['total_stay_nights'].sum() if 'total_stay_nights' in df.columns else 0
    canceled_room_nights = df[df['is_canceled'] == 1]['total_stay_nights'].sum() if 'total_stay_nights' in df.columns else 0
    metrics['estimated_occupancy_rate'] = (total_room_nights - canceled_room_nights) / total_room_nights if total_room_nights > 0 else 0
    
    return metrics