"""
Utilidades para carga y procesamiento de datos
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional

def load_hotel_data(path: str = "data/hotel_bookings_modified.csv") -> pd.DataFrame:
    """
    Carga el dataset de reservas hoteleras con tipos de datos optimizados.
    
    Parameters
    ----------
    path : str
        Ruta al archivo CSV
        
    Returns
    -------
    pd.DataFrame
        DataFrame con datos de reservas
    """
    # Cargar datos sin especificar tipos primero
    df = pd.read_csv(path)
    
    # Convertir tipos de datos de manera segura
    categorical_cols = ['hotel', 'arrival_date_month', 'meal', 'country', 
                       'market_segment', 'distribution_channel', 
                       'reserved_room_type', 'assigned_room_type',
                       'deposit_type', 'customer_type', 'reservation_status']
    
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    # Convertir columnas numéricas de manera segura
    int_cols = ['is_canceled', 'arrival_date_week_number', 'arrival_date_day_of_month',
                'stays_in_weekend_nights', 'stays_in_week_nights', 'adults', 'babies',
                'is_repeated_guest', 'previous_cancellations', 'previous_bookings_not_canceled',
                'booking_changes', 'required_car_parking_spaces', 'total_of_special_requests']
    
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int32')
    
    # Columnas float
    float_cols = ['arrival_date_year', 'children', 'adr', 'days_in_waiting_list', 'lead_time']
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convertir columna de fecha de reserva si existe
    if 'reservation_status_date' in df.columns:
        df['reservation_status_date'] = pd.to_datetime(df['reservation_status_date'], errors='coerce')
    
    return df

def load_data_dictionary(path: str = "data/Hotel Bookings Demand Data Dictionary.xlsx") -> pd.DataFrame:
    """
    Carga el diccionario de datos desde Excel.
    
    Parameters
    ----------
    path : str
        Ruta al archivo Excel
        
    Returns
    -------
    pd.DataFrame
        DataFrame con diccionario de variables
    """
    try:
        df_dict = pd.read_excel(path, engine='openpyxl')
        return df_dict
    except Exception as e:
        print(f"Error al cargar diccionario: {e}")
        return pd.DataFrame()

def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea variables derivadas útiles para el análisis.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame original
        
    Returns
    -------
    pd.DataFrame
        DataFrame con nuevas variables
    """
    df = df.copy()
    
    # Total de huéspedes
    df['total_guests'] = df['adults'] + df['children'].fillna(0) + df['babies']
    
    # Total de noches de estadía
    df['total_stay_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    
    # Categorías de lead time
    df['lead_time_bucket'] = pd.cut(
        df['lead_time'],
        bins=[0, 7, 14, 30, 60, 90, 180, 365, np.inf],
        labels=['0-7', '8-14', '15-30', '31-60', '61-90', '91-180', '181-365', '>365'],
        right=True
    )
    
    # Es hotel de ciudad
    df['is_city_hotel'] = (df['hotel'] == 'City Hotel').astype('int8')
    
    # Es reserva familiar (tiene niños o bebés)
    df['is_family'] = ((df['children'].fillna(0) > 0) | (df['babies'] > 0)).astype('int8')
    
    # Diferencia entre tipo de habitación asignada y reservada
    if 'assigned_room_type' in df.columns and 'reserved_room_type' in df.columns:
        # Convertir a string para comparación segura
        df['room_type_diff'] = (df['assigned_room_type'].astype(str) != df['reserved_room_type'].astype(str)).astype('int32')
    
    # Temporada basada en mes
    season_map = {
        'January': 'Winter', 'February': 'Winter', 'March': 'Spring',
        'April': 'Spring', 'May': 'Spring', 'June': 'Summer',
        'July': 'Summer', 'August': 'Summer', 'September': 'Fall',
        'October': 'Fall', 'November': 'Fall', 'December': 'Winter'
    }
    df['season'] = df['arrival_date_month'].map(season_map)
    
    # Categoría de ADR (precio)
    if 'adr' in df.columns and df['adr'].notna().any():
        df['adr_category'] = pd.qcut(
            df[df['adr'] > 0]['adr'],
            q=4,
            labels=['Budget', 'Economy', 'Standard', 'Premium'],
            duplicates='drop'
        )
    
    # Duración de estadía categorizada
    df['stay_duration_category'] = pd.cut(
        df['total_stay_nights'],
        bins=[0, 1, 3, 7, 14, np.inf],
        labels=['1 night', '2-3 nights', '4-7 nights', '8-14 nights', '>14 nights'],
        right=True
    )
    
    return df

def get_data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un reporte de calidad de datos.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame a analizar
        
    Returns
    -------
    pd.DataFrame
        Reporte con estadísticas de calidad
    """
    report = pd.DataFrame({
        'column': df.columns,
        'dtype': df.dtypes.astype(str),
        'n_missing': df.isnull().sum(),
        'pct_missing': (df.isnull().sum() / len(df) * 100).round(2),
        'n_unique': df.nunique(),
        'pct_unique': (df.nunique() / len(df) * 100).round(2)
    })
    
    # Agregar estadísticas para columnas numéricas
    numeric_cols = df.select_dtypes(include=['int', 'float']).columns
    for col in numeric_cols:
        if col in df.columns:
            report.loc[report['column'] == col, 'mean'] = df[col].mean()
            report.loc[report['column'] == col, 'median'] = df[col].median()
            report.loc[report['column'] == col, 'std'] = df[col].std()
            report.loc[report['column'] == col, 'min'] = df[col].min()
            report.loc[report['column'] == col, 'max'] = df[col].max()
    
    return report.sort_values('pct_missing', ascending=False)

def clean_data(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Limpia y preprocesa el dataset.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame original
    verbose : bool
        Si imprimir información del proceso
        
    Returns
    -------
    pd.DataFrame
        DataFrame limpio
    """
    df = df.copy()
    initial_shape = df.shape
    
    # Eliminar duplicados completos
    df = df.drop_duplicates()
    
    # Corregir valores negativos o anómalos en ADR
    if 'adr' in df.columns:
        # Eliminar ADR negativos o extremadamente altos
        df = df[(df['adr'] >= 0) & (df['adr'] < 5000)]
    
    # Corregir valores faltantes en children
    if 'children' in df.columns:
        df['children'] = df['children'].fillna(0)
    
    # Eliminar reservas con 0 adultos y 0 niños
    if 'adults' in df.columns and 'children' in df.columns:
        df = df[(df['adults'] > 0) | (df['children'] > 0)]
    
    # Eliminar estadías de 0 noches
    if 'stays_in_weekend_nights' in df.columns and 'stays_in_week_nights' in df.columns:
        df = df[(df['stays_in_weekend_nights'] + df['stays_in_week_nights']) > 0]
    
    if verbose:
        print(f"Forma inicial: {initial_shape}")
        print(f"Forma final: {df.shape}")
        print(f"Registros eliminados: {initial_shape[0] - df.shape[0]}")
    
    return df

def save_processed_data(df: pd.DataFrame, path: str = "data/hotel_bookings_processed.csv"):
    """
    Guarda el dataset procesado.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame a guardar
    path : str
        Ruta de destino
    """
    df.to_csv(path, index=False)
    print(f"Datos guardados en: {path}")