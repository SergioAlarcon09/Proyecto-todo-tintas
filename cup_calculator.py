"""
cup_calculator.py - Cálculos Volumétricos para Cups de Tinta

Este módulo implementa cálculos precisos de volumen para cups de tinta
de tatuaje con forma de tronco de cono invertido.

Fórmulas implementadas:
- Volumen de tronco de cono: V = (π * h / 3) * (R² + R*r + r²)
- Conversión de mm a metros para cálculos exactos
- Estimación de gotas: 1 gota ≈ 0.05ml
"""

import math
from typing import Dict, Tuple
from dataclasses import dataclass


# Constante: tamaño promedio de una gota de tinta para tatuaje en ml
DROP_SIZE_ML = 0.05


@dataclass
class CupDimensions:
    """
    Dimensiones de un cup de tinta para tatuaje.
    
    Attributes:
        name: Nombre del tamaño (XL, L, M, S)
        bottom_diameter_mm: Diámetro inferior en milímetros
        top_diameter_mm: Diámetro superior en milímetros
        height_mm: Altura en milímetros
    """
    name: str
    bottom_diameter_mm: float
    top_diameter_mm: float
    height_mm: float
    
    @property
    def bottom_radius_mm(self) -> float:
        """Radio inferior en mm."""
        return self.bottom_diameter_mm / 2
    
    @property
    def top_radius_mm(self) -> float:
        """Radio superior en mm."""
        return self.top_diameter_mm / 2


# Especificaciones de cups basadas en la imagen de referencia
# Nota: Los cups tienen forma de tronco de cono con la base más ancha arriba
CUP_SPECS: Dict[str, CupDimensions] = {
    'XL': CupDimensions('XL', bottom_diameter_mm=20.0, top_diameter_mm=23.3, height_mm=17.0),
    'L': CupDimensions('L', bottom_diameter_mm=17.0, top_diameter_mm=18.6, height_mm=14.0),
    'M': CupDimensions('M', bottom_diameter_mm=14.0, top_diameter_mm=17.1, height_mm=12.0),
    'S': CupDimensions('S', bottom_diameter_mm=11.0, top_diameter_mm=12.3, height_mm=10.0),
}


def calculate_frustum_volume(R: float, r: float, h: float) -> float:
    """
    Calcula el volumen de un tronco de cono (frustum).
    
    Fórmula: V = (π * h / 3) * (R² + R*r + r²)
    
    Args:
        R: Radio mayor (parte superior del cup) en la unidad deseada
        r: Radio menor (parte inferior del cup) en la unidad deseada
        h: Altura del tronco de cono en la misma unidad
    
    Returns:
        Volumen en unidades cúbicas de la misma unidad de entrada
    """
    return (math.pi * h / 3) * (R**2 + R*r + r**2)


def calculate_cup_volume_ml(cup_size: str) -> float:
    """
    Calcula el volumen total de un cup en mililitros.
    
    Args:
        cup_size: Tamaño del cup ('XL', 'L', 'M', 'S')
    
    Returns:
        Volumen en mililitros
    
    Raises:
        ValueError: Si el tamaño de cup no es válido
    """
    if cup_size not in CUP_SPECS:
        raise ValueError(f"Tamaño de cup inválido: {cup_size}. Use: {list(CUP_SPECS.keys())}")
    
    cup = CUP_SPECS[cup_size]
    
    # Convertir mm a cm para obtener resultado en cm³ = ml
    R = cup.top_radius_mm / 10.0  # Radio mayor en cm
    r = cup.bottom_radius_mm / 10.0  # Radio menor en cm
    h = cup.height_mm / 10.0  # Altura en cm
    
    # Volumen en cm³ = ml
    volume_ml = calculate_frustum_volume(R, r, h)
    
    return volume_ml


def calculate_fill_volume_ml(cup_size: str, fill_percentage: float) -> float:
    """
    Calcula el volumen de tinta dado un porcentaje de llenado.
    
    Considera que el llenado es lineal en altura, lo cual afecta
    el volumen de manera no lineal debido a la forma cónica.
    
    Args:
        cup_size: Tamaño del cup ('XL', 'L', 'M', 'S')
        fill_percentage: Porcentaje de llenado (0-100)
    
    Returns:
        Volumen de tinta en mililitros
    """
    if cup_size not in CUP_SPECS:
        raise ValueError(f"Tamaño de cup inválido: {cup_size}")
    
    fill_percentage = max(0, min(100, fill_percentage))
    fill_ratio = fill_percentage / 100.0
    
    cup = CUP_SPECS[cup_size]
    
    # Dimensiones en cm
    R_top = cup.top_radius_mm / 10.0  # Radio en la parte superior
    r_bottom = cup.bottom_radius_mm / 10.0  # Radio en la base
    h_total = cup.height_mm / 10.0  # Altura total
    
    # Altura de llenado
    h_fill = h_total * fill_ratio
    
    # Radio en el nivel de llenado (interpolación lineal)
    # El radio aumenta linealmente desde r_bottom hasta R_top
    r_fill = r_bottom + (R_top - r_bottom) * fill_ratio
    
    # Volumen del tronco de cono desde la base hasta el nivel de llenado
    volume_ml = calculate_frustum_volume(r_fill, r_bottom, h_fill)
    
    return volume_ml


def calculate_total_drops(cup_size: str, fill_percentage: float = 100) -> int:
    """
    Calcula el número total de gotas que caben en un cup.
    
    Args:
        cup_size: Tamaño del cup ('XL', 'L', 'M', 'S')
        fill_percentage: Porcentaje de llenado (0-100)
    
    Returns:
        Número de gotas (entero redondeado)
    """
    volume_ml = calculate_fill_volume_ml(cup_size, fill_percentage)
    drops = volume_ml / DROP_SIZE_ML
    return int(round(drops))


def get_cup_info(cup_size: str) -> Dict:
    """
    Obtiene información completa sobre un tamaño de cup.
    
    Args:
        cup_size: Tamaño del cup ('XL', 'L', 'M', 'S')
    
    Returns:
        Diccionario con toda la información del cup
    """
    if cup_size not in CUP_SPECS:
        raise ValueError(f"Tamaño de cup inválido: {cup_size}")
    
    cup = CUP_SPECS[cup_size]
    total_volume = calculate_cup_volume_ml(cup_size)
    total_drops = calculate_total_drops(cup_size, 100)
    
    return {
        'name': cup.name,
        'bottom_diameter_mm': cup.bottom_diameter_mm,
        'top_diameter_mm': cup.top_diameter_mm,
        'height_mm': cup.height_mm,
        'volume_ml': round(total_volume, 3),
        'max_drops': total_drops
    }


def get_all_cup_sizes() -> list:
    """
    Retorna lista de todos los tamaños de cup disponibles.
    
    Returns:
        Lista de tamaños ['XL', 'L', 'M', 'S']
    """
    return list(CUP_SPECS.keys())


def calculate_drops_for_percentages(cup_size: str, fill_percentage: float,
                                    color_proportions: Dict[str, float]) -> Dict[str, int]:
    """
    Calcula las gotas necesarias de cada color para llenar un cup.
    
    Args:
        cup_size: Tamaño del cup ('XL', 'L', 'M', 'S')
        fill_percentage: Porcentaje de llenado (0-100)
        color_proportions: Dict con proporciones de colores (valores 0-1)
    
    Returns:
        Dict con número de gotas por cada color
    """
    total_drops = calculate_total_drops(cup_size, fill_percentage)
    
    # Normalizar proporciones
    total_proportion = sum(color_proportions.values())
    if total_proportion == 0:
        return {color: 0 for color in color_proportions}
    
    result = {}
    drops_assigned = 0
    sorted_colors = sorted(color_proportions.items(), key=lambda x: x[1], reverse=True)
    
    for i, (color, proportion) in enumerate(sorted_colors):
        if i == len(sorted_colors) - 1:
            # Último color: asignar gotas restantes para mantener suma exacta
            drops = total_drops - drops_assigned
        else:
            normalized_prop = proportion / total_proportion
            drops = int(round(normalized_prop * total_drops))
        
        result[color] = max(0, drops)
        drops_assigned += result[color]
    
    return result


# Información de ejemplo para documentación
if __name__ == "__main__":
    print("=== Información de Cups de Tinta para Tatuaje ===\n")
    
    for size in get_all_cup_sizes():
        info = get_cup_info(size)
        print(f"Tamaño {size}:")
        print(f"  Diámetro superior: {info['top_diameter_mm']}mm")
        print(f"  Diámetro inferior: {info['bottom_diameter_mm']}mm")
        print(f"  Altura: {info['height_mm']}mm")
        print(f"  Volumen: {info['volume_ml']}ml")
        print(f"  Gotas máximas: {info['max_drops']}")
        print()
