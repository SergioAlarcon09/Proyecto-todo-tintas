"""
gui_components.py - Componentes Personalizados de GUI

Este módulo implementa widgets personalizados para la aplicación de mezcla de tintas:
- Rueda cromática interactiva personalizada
- Widget circular para selección de colores HSV
- Visualización en tiempo real del color seleccionado
- Integración fluida con cálculos de mezcla
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Callable, Optional, Tuple

from utils import hsv_to_rgb, rgb_to_hsv, rgb_to_hex


class ColorWheel(tk.Canvas):
    """
    Rueda cromática interactiva para selección de colores HSV.
    
    Permite al usuario seleccionar colores mediante:
    - Click y arrastre en la rueda circular para tono y saturación
    - Slider separado para el brillo (valor)
    """
    
    def __init__(self, master, size: int = 200, 
                 on_color_change: Optional[Callable[[int, int, int], None]] = None,
                 **kwargs):
        """
        Inicializa la rueda cromática.
        
        Args:
            master: Widget padre
            size: Tamaño del widget en píxeles
            on_color_change: Callback cuando cambia el color (recibe r, g, b)
        """
        super().__init__(master, width=size, height=size, 
                        highlightthickness=0, **kwargs)
        
        self.size = size
        self.radius = (size - 10) // 2
        self.center = size // 2
        self.on_color_change = on_color_change
        
        # Estado actual HSV
        self.hue = 0.0  # 0-360
        self.saturation = 1.0  # 0-1
        self.value = 1.0  # 0-1
        
        # Selector
        self.selector_radius = 8
        self.selector = None
        
        # Dibujar rueda
        self._draw_wheel()
        self._draw_selector()
        
        # Eventos
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
    
    def _draw_wheel(self):
        """Dibuja la rueda de colores usando círculos concéntricos."""
        self.delete("wheel")
        
        # Dibujar la rueda usando líneas desde el centro
        for angle in range(360):
            for r in range(1, self.radius + 1):
                # Calcular saturación basada en la distancia al centro
                sat = r / self.radius
                
                # Convertir HSV a RGB
                rgb = hsv_to_rgb(angle, sat, self.value)
                color = rgb_to_hex(*rgb)
                
                # Calcular posición
                rad = math.radians(angle)
                x = self.center + r * math.cos(rad)
                y = self.center - r * math.sin(rad)  # Y invertida
                
                # Dibujar punto
                self.create_oval(x-1, y-1, x+1, y+1, fill=color, 
                               outline=color, tags="wheel")
    
    def _draw_selector(self):
        """Dibuja el selector de posición actual."""
        if self.selector:
            self.delete(self.selector)
        
        # Calcular posición del selector
        r = self.saturation * self.radius
        rad = math.radians(self.hue)
        x = self.center + r * math.cos(rad)
        y = self.center - r * math.sin(rad)
        
        # Dibujar selector (círculo con borde)
        self.selector = self.create_oval(
            x - self.selector_radius, y - self.selector_radius,
            x + self.selector_radius, y + self.selector_radius,
            outline="black", width=2, fill="", tags="selector"
        )
        
        # Círculo interior blanco
        self.create_oval(
            x - self.selector_radius + 2, y - self.selector_radius + 2,
            x + self.selector_radius - 2, y + self.selector_radius - 2,
            outline="white", width=1, fill="", tags="selector"
        )
    
    def _on_click(self, event):
        """Maneja click en la rueda."""
        self._update_from_position(event.x, event.y)
    
    def _on_drag(self, event):
        """Maneja arrastre en la rueda."""
        self._update_from_position(event.x, event.y)
    
    def _update_from_position(self, x: int, y: int):
        """Actualiza el color basado en posición del mouse."""
        # Calcular distancia y ángulo desde el centro
        dx = x - self.center
        dy = self.center - y  # Y invertida
        
        distance = math.sqrt(dx**2 + dy**2)
        angle = math.degrees(math.atan2(dy, dx))
        
        if angle < 0:
            angle += 360
        
        # Limitar distancia al radio
        distance = min(distance, self.radius)
        
        # Actualizar valores
        self.hue = angle
        self.saturation = distance / self.radius
        
        # Redibujar selector
        self.delete("selector")
        self._draw_selector()
        
        # Notificar cambio
        self._notify_change()
    
    def _notify_change(self):
        """Notifica el cambio de color al callback."""
        if self.on_color_change:
            rgb = hsv_to_rgb(self.hue, self.saturation, self.value)
            self.on_color_change(*rgb)
    
    def set_value(self, value: float):
        """
        Establece el brillo (Value en HSV).
        
        Args:
            value: Brillo de 0 a 1
        """
        self.value = max(0, min(1, value))
        self._draw_wheel()
        self._draw_selector()
        self._notify_change()
    
    def set_color_rgb(self, r: int, g: int, b: int):
        """
        Establece el color actual usando valores RGB.
        
        Args:
            r: Rojo (0-255)
            g: Verde (0-255)
            b: Azul (0-255)
        """
        h, s, v = rgb_to_hsv(r, g, b)
        self.hue = h
        self.saturation = s
        self.value = v
        self._draw_wheel()
        self._draw_selector()
    
    def get_color_rgb(self) -> Tuple[int, int, int]:
        """
        Obtiene el color actual como RGB.
        
        Returns:
            Tupla (r, g, b)
        """
        return hsv_to_rgb(self.hue, self.saturation, self.value)
    
    def get_color_hsv(self) -> Tuple[float, float, float]:
        """
        Obtiene el color actual como HSV.
        
        Returns:
            Tupla (h, s, v) donde h está en grados
        """
        return (self.hue, self.saturation, self.value)


class ColorPreview(tk.Frame):
    """
    Widget para mostrar vista previa del color seleccionado y el resultado.
    """
    
    def __init__(self, master, size: int = 80, **kwargs):
        """
        Inicializa el widget de vista previa.
        
        Args:
            master: Widget padre
            size: Tamaño del cuadro de color
        """
        super().__init__(master, **kwargs)
        
        self.size = size
        
        # Color objetivo
        self.target_frame = tk.LabelFrame(self, text="Color Objetivo", 
                                          padx=5, pady=5)
        self.target_frame.pack(side=tk.LEFT, padx=5)
        
        self.target_canvas = tk.Canvas(self.target_frame, width=size, height=size,
                                       highlightthickness=1, highlightbackground="gray")
        self.target_canvas.pack()
        
        self.target_label = tk.Label(self.target_frame, text="#FFFFFF", 
                                    font=("Courier", 10))
        self.target_label.pack()
        
        # Color resultado (aproximación)
        self.result_frame = tk.LabelFrame(self, text="Resultado Mezcla", 
                                          padx=5, pady=5)
        self.result_frame.pack(side=tk.LEFT, padx=5)
        
        self.result_canvas = tk.Canvas(self.result_frame, width=size, height=size,
                                       highlightthickness=1, highlightbackground="gray")
        self.result_canvas.pack()
        
        self.result_label = tk.Label(self.result_frame, text="#FFFFFF", 
                                    font=("Courier", 10))
        self.result_label.pack()
        
        # Inicializar en blanco
        self.set_target_color(255, 255, 255)
        self.set_result_color(255, 255, 255)
    
    def set_target_color(self, r: int, g: int, b: int):
        """Establece el color objetivo."""
        color = rgb_to_hex(r, g, b)
        self.target_canvas.configure(bg=color)
        self.target_label.configure(text=color.upper())
    
    def set_result_color(self, r: int, g: int, b: int):
        """Establece el color resultado de la mezcla."""
        color = rgb_to_hex(r, g, b)
        self.result_canvas.configure(bg=color)
        self.result_label.configure(text=color.upper())


class CupVisualizer(tk.Canvas):
    """
    Widget para visualizar el cup de tinta con nivel de llenado.
    """
    
    def __init__(self, master, width: int = 100, height: int = 120, **kwargs):
        """
        Inicializa el visualizador de cup.
        
        Args:
            master: Widget padre
            width: Ancho del canvas
            height: Alto del canvas
        """
        super().__init__(master, width=width, height=height, 
                        highlightthickness=0, **kwargs)
        
        self.cup_width = width
        self.cup_height = height
        self.fill_percentage = 100
        self.cup_size = 'M'
        
        # Colores
        self.cup_color = "#E0E0E0"
        self.ink_color = "#000000"
        
        self._draw_cup()
    
    def _draw_cup(self):
        """Dibuja el cup con el nivel de llenado actual."""
        self.delete("all")
        
        # Márgenes
        margin = 10
        
        # Dimensiones del cup en el canvas
        cup_top_width = self.cup_width - 2 * margin
        cup_bottom_width = int(cup_top_width * 0.7)
        cup_height = self.cup_height - 2 * margin
        
        # Puntos del trapecio (cup)
        center_x = self.cup_width // 2
        top_y = margin
        bottom_y = self.cup_height - margin
        
        points = [
            center_x - cup_top_width // 2, top_y,      # Arriba izquierda
            center_x + cup_top_width // 2, top_y,      # Arriba derecha
            center_x + cup_bottom_width // 2, bottom_y,  # Abajo derecha
            center_x - cup_bottom_width // 2, bottom_y,  # Abajo izquierda
        ]
        
        # Dibujar cup vacío
        self.create_polygon(points, fill=self.cup_color, outline="gray", 
                           width=2, tags="cup")
        
        # Calcular nivel de llenado
        if self.fill_percentage > 0:
            fill_ratio = self.fill_percentage / 100
            fill_height = cup_height * fill_ratio
            
            # Calcular ancho en el nivel de llenado (interpolación lineal)
            fill_y = bottom_y - fill_height
            width_at_fill = cup_bottom_width + (cup_top_width - cup_bottom_width) * fill_ratio
            
            ink_points = [
                center_x - width_at_fill // 2, fill_y,
                center_x + width_at_fill // 2, fill_y,
                center_x + cup_bottom_width // 2, bottom_y,
                center_x - cup_bottom_width // 2, bottom_y,
            ]
            
            self.create_polygon(ink_points, fill=self.ink_color, 
                              outline="", tags="ink")
        
        # Etiqueta de tamaño
        self.create_text(center_x, self.cup_height - 5, text=self.cup_size,
                        font=("Arial", 10, "bold"), tags="label")
    
    def set_fill_percentage(self, percentage: float):
        """Establece el porcentaje de llenado."""
        self.fill_percentage = max(0, min(100, percentage))
        self._draw_cup()
    
    def set_cup_size(self, size: str):
        """Establece el tamaño del cup."""
        self.cup_size = size
        self._draw_cup()
    
    def set_ink_color(self, r: int, g: int, b: int):
        """Establece el color de la tinta mostrada."""
        self.ink_color = rgb_to_hex(r, g, b)
        self._draw_cup()


class DropsDisplay(tk.Frame):
    """
    Widget para mostrar las gotas necesarias de cada color primario.
    """
    
    def __init__(self, master, **kwargs):
        """
        Inicializa el display de gotas.
        
        Args:
            master: Widget padre
        """
        super().__init__(master, **kwargs)
        
        # Configurar grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        
        # Crear indicadores para cada color
        self.colors = {
            'amarillo': {'rgb': '#FFD700', 'label': 'Amarillo', 'row': 0},
            'azul': {'rgb': '#0066CC', 'label': 'Azul', 'row': 1},
            'rojo': {'rgb': '#CC0000', 'label': 'Rojo', 'row': 2},
        }
        
        self.drop_labels = {}
        
        for color, info in self.colors.items():
            # Frame para cada color
            frame = tk.Frame(self)
            frame.grid(row=info['row'], column=0, columnspan=3, 
                      sticky="ew", pady=5, padx=10)
            
            # Indicador de color
            color_box = tk.Canvas(frame, width=30, height=30, 
                                 highlightthickness=1, highlightbackground="gray")
            color_box.create_rectangle(0, 0, 30, 30, fill=info['rgb'], outline="")
            color_box.pack(side=tk.LEFT, padx=(0, 10))
            
            # Nombre del color
            name_label = tk.Label(frame, text=info['label'], 
                                 font=("Arial", 11), width=10, anchor="w")
            name_label.pack(side=tk.LEFT)
            
            # Número de gotas
            drops_label = tk.Label(frame, text="0 gotas", 
                                  font=("Arial", 14, "bold"), width=10)
            drops_label.pack(side=tk.RIGHT)
            
            self.drop_labels[color] = drops_label
        
        # Total de gotas
        separator = ttk.Separator(self, orient="horizontal")
        separator.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        
        total_frame = tk.Frame(self)
        total_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10)
        
        tk.Label(total_frame, text="TOTAL:", font=("Arial", 12, "bold"),
                width=15, anchor="w").pack(side=tk.LEFT)
        self.total_label = tk.Label(total_frame, text="0 gotas", 
                                   font=("Arial", 14, "bold"))
        self.total_label.pack(side=tk.RIGHT)
    
    def set_drops(self, amarillo: int, azul: int, rojo: int):
        """
        Establece el número de gotas para cada color.
        
        Args:
            amarillo: Gotas de amarillo
            azul: Gotas de azul
            rojo: Gotas de rojo
        """
        self.drop_labels['amarillo'].configure(text=f"{amarillo} gotas")
        self.drop_labels['azul'].configure(text=f"{azul} gotas")
        self.drop_labels['rojo'].configure(text=f"{rojo} gotas")
        
        total = amarillo + azul + rojo
        self.total_label.configure(text=f"{total} gotas")


class Tooltip:
    """
    Clase para crear tooltips informativos.
    """
    
    def __init__(self, widget, text: str):
        """
        Inicializa el tooltip.
        
        Args:
            widget: Widget al que asociar el tooltip
            text: Texto del tooltip
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)
    
    def _show(self, event=None):
        """Muestra el tooltip."""
        # Position tooltip relative to widget's screen position
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("Arial", 9))
        label.pack()
    
    def _hide(self, event=None):
        """Oculta el tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
