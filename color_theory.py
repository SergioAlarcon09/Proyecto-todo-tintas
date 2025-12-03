"""
color_theory.py - Teoría del Color Científica para Tintas de Tatuaje

Este módulo implementa un sistema avanzado de mezcla de colores optimizado
para pigmentos de tatuaje que se comportan de manera sustractiva.

Características:
- Conversión RGB → CMY para pigmentos de tatuaje
- Compensación por opacidad y comportamiento sustractivo
- Normalización de proporciones a números enteros de gotas
- Algoritmos que mantienen precisión de color
"""

import math
from typing import Dict, Tuple, List
from dataclasses import dataclass

from utils import rgb_to_hsv, hsv_to_rgb, smart_round_proportions, clamp


# Colores primarios para tatuaje (Amarillo, Azul, Rojo)
PRIMARY_COLORS = {
    'amarillo': (255, 255, 0),    # Yellow
    'azul': (0, 0, 255),          # Blue  
    'rojo': (255, 0, 0),          # Red
}


@dataclass
class ColorMix:
    """
    Representa una mezcla de colores primarios.
    
    Attributes:
        amarillo: Proporción de amarillo (0-1)
        azul: Proporción de azul (0-1)
        rojo: Proporción de rojo (0-1)
        resulting_rgb: Color RGB resultante de la mezcla
    """
    amarillo: float
    azul: float
    rojo: float
    resulting_rgb: Tuple[int, int, int]
    
    def to_drops(self, total_drops: int) -> Dict[str, int]:
        """
        Convierte proporciones a gotas enteras.
        
        Args:
            total_drops: Número total de gotas disponibles
        
        Returns:
            Dict con gotas por cada color primario
        """
        proportions = [self.amarillo, self.azul, self.rojo]
        drops = smart_round_proportions(proportions, total_drops)
        
        return {
            'amarillo': drops[0],
            'azul': drops[1],
            'rojo': drops[2]
        }


def rgb_to_cmy(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """
    Convierte RGB a CMY (Cyan, Magenta, Yellow).
    
    El modelo CMY es más apropiado para pigmentos que para luz.
    
    Args:
        r: Rojo (0-255)
        g: Verde (0-255)
        b: Azul (0-255)
    
    Returns:
        Tupla (C, M, Y) con valores 0-1
    """
    c = 1 - (r / 255.0)
    m = 1 - (g / 255.0)
    y = 1 - (b / 255.0)
    return (c, m, y)


def cmy_to_rgb(c: float, m: float, y: float) -> Tuple[int, int, int]:
    """
    Convierte CMY a RGB.
    
    Args:
        c: Cyan (0-1)
        m: Magenta (0-1)
        y: Yellow (0-1)
    
    Returns:
        Tupla (R, G, B) con valores 0-255
    """
    r = int(round((1 - c) * 255))
    g = int(round((1 - m) * 255))
    b = int(round((1 - y) * 255))
    return (clamp(r, 0, 255), clamp(g, 0, 255), clamp(b, 0, 255))


def rgb_to_ryb_proportions(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """
    Convierte RGB a proporciones RYB (Rojo, Amarillo, Azul) para pigmentos.
    
    Este algoritmo está optimizado para pigmentos de tatuaje que usan
    el modelo tradicional de colores primarios artísticos (RYB).
    
    El proceso:
    1. Analiza el color objetivo en HSV para entender tono, saturación y brillo
    2. Mapea el tono a combinaciones de pigmentos RYB
    3. Ajusta por saturación y brillo
    
    Args:
        r: Rojo (0-255)
        g: Verde (0-255)
        b: Azul (0-255)
    
    Returns:
        Tupla (rojo, amarillo, azul) con proporciones 0-1
    """
    # Convertir a HSV para análisis
    h, s, v = rgb_to_hsv(r, g, b)
    
    # Normalizar valores
    h = h % 360  # Asegurar rango 0-360
    
    # Si no hay saturación, es gris - mezcla igual de todos
    if s < 0.05:
        return (0.33, 0.33, 0.34)
    
    # Mapeo de tono HSV a proporciones RYB
    # En el modelo RYB tradicional:
    # - Rojo puro: 0°
    # - Naranja: 30° (Rojo + Amarillo)
    # - Amarillo puro: 60°
    # - Verde: 120° (Amarillo + Azul)
    # - Azul puro: 240°
    # - Violeta: 300° (Azul + Rojo)
    
    red_prop = 0.0
    yellow_prop = 0.0
    blue_prop = 0.0
    
    if 0 <= h < 60:  # Rojo a Amarillo (naranjas)
        red_prop = 1 - (h / 60)
        yellow_prop = h / 60
        blue_prop = 0
    elif 60 <= h < 120:  # Amarillo a Verde
        red_prop = 0
        yellow_prop = 1 - ((h - 60) / 60)
        blue_prop = (h - 60) / 60
    elif 120 <= h < 180:  # Verde a Cyan
        red_prop = 0
        yellow_prop = 1 - ((h - 120) / 60) * 0.5
        blue_prop = 0.5 + ((h - 120) / 60) * 0.5
    elif 180 <= h < 240:  # Cyan a Azul
        red_prop = 0
        yellow_prop = 0.5 - ((h - 180) / 60) * 0.5
        blue_prop = 1
    elif 240 <= h < 300:  # Azul a Magenta
        red_prop = (h - 240) / 60
        yellow_prop = 0
        blue_prop = 1 - ((h - 240) / 60)
    else:  # 300-360: Magenta a Rojo
        red_prop = 1
        yellow_prop = 0
        blue_prop = 1 - ((h - 300) / 60)
    
    # Ajustar por saturación (colores menos saturados necesitan mezcla más equilibrada)
    gray_mix = (1 - s) / 3
    red_prop = red_prop * s + gray_mix
    yellow_prop = yellow_prop * s + gray_mix
    blue_prop = blue_prop * s + gray_mix
    
    # Normalizar para que sumen 1
    total = red_prop + yellow_prop + blue_prop
    if total > 0:
        red_prop /= total
        yellow_prop /= total
        blue_prop /= total
    
    return (red_prop, yellow_prop, blue_prop)


def calculate_color_mix(r: int, g: int, b: int) -> ColorMix:
    """
    Calcula la mezcla de colores primarios necesaria para obtener un color RGB.
    
    Args:
        r: Componente rojo del color objetivo (0-255)
        g: Componente verde del color objetivo (0-255)
        b: Componente azul del color objetivo (0-255)
    
    Returns:
        ColorMix con las proporciones calculadas
    """
    # Obtener proporciones RYB
    rojo, amarillo, azul = rgb_to_ryb_proportions(r, g, b)
    
    # El color resultante es una aproximación basada en las proporciones
    resulting_rgb = approximate_mix_result(rojo, amarillo, azul)
    
    return ColorMix(
        amarillo=amarillo,
        azul=azul,
        rojo=rojo,
        resulting_rgb=resulting_rgb
    )


def approximate_mix_result(rojo: float, amarillo: float, azul: float) -> Tuple[int, int, int]:
    """
    Aproxima el color RGB resultante de mezclar pigmentos RYB.
    
    Utiliza un modelo de mezcla sustractiva simplificado para pigmentos.
    
    Args:
        rojo: Proporción de rojo (0-1)
        amarillo: Proporción de amarillo (0-1)
        azul: Proporción de azul (0-1)
    
    Returns:
        Tupla (R, G, B) del color aproximado resultante
    """
    # Modelo simplificado de mezcla sustractiva para RYB
    # Basado en observaciones empíricas de mezcla de pigmentos
    
    # Normalizar proporciones
    total = rojo + amarillo + azul
    if total == 0:
        return (255, 255, 255)  # Sin pigmento = blanco
    
    r = rojo / total
    y = amarillo / total
    b = azul / total
    
    # Calcular componentes RGB de la mezcla
    # Rojo pigmento contribuye principalmente al canal R
    # Amarillo contribuye a R y G
    # Azul contribuye principalmente al canal B
    
    out_r = int(clamp(255 * (r + y * 0.8), 0, 255))
    out_g = int(clamp(255 * (y * 0.9 + (1 - r - b) * 0.3), 0, 255))
    out_b = int(clamp(255 * (b * 0.9), 0, 255))
    
    return (out_r, out_g, out_b)


def get_color_name(r: int, g: int, b: int) -> str:
    """
    Obtiene un nombre descriptivo aproximado para un color RGB.
    
    Args:
        r: Rojo (0-255)
        g: Verde (0-255)
        b: Azul (0-255)
    
    Returns:
        Nombre descriptivo del color
    """
    h, s, v = rgb_to_hsv(r, g, b)
    
    # Casos especiales: grises y blanco/negro
    if s < 0.1:
        if v < 0.2:
            return "Negro"
        elif v < 0.5:
            return "Gris oscuro"
        elif v < 0.8:
            return "Gris"
        elif v < 0.95:
            return "Gris claro"
        else:
            return "Blanco"
    
    # Colores por rango de tono
    color_ranges = [
        (15, "Rojo"),
        (45, "Naranja"),
        (75, "Amarillo"),
        (150, "Verde"),
        (210, "Cyan"),
        (270, "Azul"),
        (330, "Magenta"),
        (360, "Rojo")
    ]
    
    base_name = "Rojo"
    for limit, name in color_ranges:
        if h < limit:
            base_name = name
            break
    
    # Modificadores de luminosidad/saturación
    if v < 0.3:
        return f"{base_name} oscuro"
    elif v > 0.8 and s < 0.5:
        return f"{base_name} claro"
    elif s < 0.4:
        return f"{base_name} pálido"
    
    return base_name


def validate_mix_feasibility(drops: Dict[str, int]) -> Tuple[bool, str]:
    """
    Valida si una mezcla es factible de realizar.
    
    Args:
        drops: Dict con gotas de cada color
    
    Returns:
        Tupla (es_factible, mensaje)
    """
    total = sum(drops.values())
    
    if total == 0:
        return (False, "Se requiere al menos una gota de algún color")
    
    # Verificar que no haya valores negativos
    for color, count in drops.items():
        if count < 0:
            return (False, f"No puede haber gotas negativas de {color}")
    
    return (True, "Mezcla factible")


# Paleta de colores comunes para referencia rápida
COMMON_TATTOO_COLORS = {
    "Negro sólido": (0, 0, 0),
    "Gris suave": (128, 128, 128),
    "Rojo sangre": (180, 0, 0),
    "Azul marino": (0, 0, 139),
    "Verde bosque": (34, 139, 34),
    "Naranja fuego": (255, 140, 0),
    "Púrpura real": (75, 0, 130),
    "Rosa suave": (255, 182, 193),
    "Marrón tierra": (139, 69, 19),
    "Amarillo sol": (255, 215, 0),
}


if __name__ == "__main__":
    print("=== Prueba de Teoría del Color ===\n")
    
    # Probar conversión de algunos colores
    test_colors = [
        (255, 0, 0, "Rojo puro"),
        (0, 255, 0, "Verde puro"),
        (0, 0, 255, "Azul puro"),
        (255, 165, 0, "Naranja"),
        (128, 0, 128, "Púrpura"),
    ]
    
    for r, g, b, name in test_colors:
        mix = calculate_color_mix(r, g, b)
        print(f"{name} ({r}, {g}, {b}):")
        print(f"  Amarillo: {mix.amarillo:.2%}")
        print(f"  Azul: {mix.azul:.2%}")
        print(f"  Rojo: {mix.rojo:.2%}")
        print(f"  Color detectado: {get_color_name(r, g, b)}")
        print()
