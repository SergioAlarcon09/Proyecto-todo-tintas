"""
utils.py - Utilidades Matemáticas para Calculadora de Tintas

Este módulo proporciona funciones auxiliares para:
- Redondeo inteligente que preserva proporciones
- Validaciones de capacidad máxima
- Conversiones entre sistemas de color
- Funciones de optimización de mezclas
"""

import colorsys
import math
from typing import Tuple, List


def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """
    Convierte valores RGB (0-255) a HSV (H: 0-360, S: 0-1, V: 0-1).
    
    Args:
        r: Valor rojo (0-255)
        g: Valor verde (0-255)
        b: Valor azul (0-255)
    
    Returns:
        Tupla (h, s, v) donde h está en grados (0-360)
    """
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    return (h * 360, s, v)


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """
    Convierte valores HSV a RGB (0-255).
    
    Args:
        h: Tono en grados (0-360)
        s: Saturación (0-1)
        v: Valor/Brillo (0-1)
    
    Returns:
        Tupla (r, g, b) con valores 0-255
    """
    h_norm = (h % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(h_norm, s, v)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convierte valores RGB a formato hexadecimal.
    
    Args:
        r: Valor rojo (0-255)
        g: Valor verde (0-255)
        b: Valor azul (0-255)
    
    Returns:
        String en formato '#RRGGBB'
    """
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convierte color hexadecimal a RGB.
    
    Args:
        hex_color: Color en formato '#RRGGBB' o 'RRGGBB'
    
    Returns:
        Tupla (r, g, b) con valores 0-255
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def smart_round_proportions(proportions: List[float], total_drops: int) -> List[int]:
    """
    Redondeo inteligente que preserva proporciones y suma exacta.
    
    Usa el algoritmo del mayor residuo para distribuir gotas
    manteniendo las proporciones lo más cercanas posible.
    
    Args:
        proportions: Lista de proporciones decimales (deben sumar ~1)
        total_drops: Número total de gotas a distribuir
    
    Returns:
        Lista de enteros que suman exactamente total_drops
    """
    if not proportions or total_drops <= 0:
        return [0] * len(proportions) if proportions else []
    
    # Normalizar proporciones
    total_prop = sum(proportions)
    if total_prop == 0:
        return [0] * len(proportions)
    
    normalized = [p / total_prop for p in proportions]
    
    # Calcular valores exactos y base entera
    exact_values = [p * total_drops for p in normalized]
    base_values = [int(v) for v in exact_values]
    
    # Calcular residuos
    remainders = [(i, exact_values[i] - base_values[i]) 
                  for i in range(len(exact_values))]
    
    # Ordenar por residuo descendente
    remainders.sort(key=lambda x: x[1], reverse=True)
    
    # Distribuir gotas restantes
    remaining = total_drops - sum(base_values)
    for i in range(remaining):
        idx = remainders[i][0]
        base_values[idx] += 1
    
    return base_values


def validate_capacity(drops: int, max_drops: int) -> bool:
    """
    Valida que el número de gotas no exceda la capacidad.
    
    Args:
        drops: Número de gotas a validar
        max_drops: Capacidad máxima en gotas
    
    Returns:
        True si es válido, False si excede capacidad
    """
    return 0 <= drops <= max_drops


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Limita un valor dentro de un rango.
    
    Args:
        value: Valor a limitar
        min_val: Valor mínimo
        max_val: Valor máximo
    
    Returns:
        Valor limitado dentro del rango
    """
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """
    Interpolación lineal entre dos valores.
    
    Args:
        a: Valor inicial
        b: Valor final
        t: Factor de interpolación (0-1)
    
    Returns:
        Valor interpolado
    """
    return a + (b - a) * clamp(t, 0, 1)


def calculate_color_distance(rgb1: Tuple[int, int, int], 
                            rgb2: Tuple[int, int, int]) -> float:
    """
    Calcula la distancia euclidiana entre dos colores RGB.
    
    Args:
        rgb1: Primer color como tupla (r, g, b)
        rgb2: Segundo color como tupla (r, g, b)
    
    Returns:
        Distancia euclidiana (0-441.67 aproximadamente)
    """
    return math.sqrt(
        (rgb1[0] - rgb2[0]) ** 2 +
        (rgb1[1] - rgb2[1]) ** 2 +
        (rgb1[2] - rgb2[2]) ** 2
    )


def mm_to_meters(mm: float) -> float:
    """
    Convierte milímetros a metros.
    
    Args:
        mm: Valor en milímetros
    
    Returns:
        Valor en metros
    """
    return mm / 1000.0


def ml_to_drops(ml: float, drop_size_ml: float = 0.05) -> float:
    """
    Convierte mililitros a número de gotas.
    
    Args:
        ml: Volumen en mililitros
        drop_size_ml: Tamaño de una gota en ml (default: 0.05ml)
    
    Returns:
        Número de gotas (puede ser decimal)
    """
    return ml / drop_size_ml


def drops_to_ml(drops: float, drop_size_ml: float = 0.05) -> float:
    """
    Convierte número de gotas a mililitros.
    
    Args:
        drops: Número de gotas
        drop_size_ml: Tamaño de una gota en ml (default: 0.05ml)
    
    Returns:
        Volumen en mililitros
    """
    return drops * drop_size_ml
