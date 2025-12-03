"""
main.py - Aplicación Principal: Calculadora de Mezclas de Tintas para Tatuaje

Interfaz gráfica completa con tkinter que incluye:
- Selector de tamaño de cup (XL, L, M, S)
- Control deslizante para porcentaje de llenado (0-100%)
- Rueda cromática para selección de color
- Panel de resultados mostrando gotas necesarias
- Vista previa del color objetivo
- Actualización en tiempo real

Autor: Calculadora de Tintas
"""

import tkinter as tk
from tkinter import ttk
from typing import Tuple

from cup_calculator import (
    get_all_cup_sizes, get_cup_info, 
    calculate_total_drops
)
from color_theory import (
    calculate_color_mix, get_color_name
)
from gui_components import (
    ColorWheel, ColorPreview, CupVisualizer, 
    DropsDisplay, Tooltip
)
from utils import rgb_to_hex


class TattooInkCalculator(tk.Tk):
    """
    Aplicación principal para calcular mezclas de tintas de tatuaje.
    """
    
    def __init__(self):
        """Inicializa la aplicación."""
        super().__init__()
        
        self.title("🎨 Calculadora de Mezclas de Tintas para Tatuaje")
        self.geometry("800x700")
        self.minsize(700, 600)
        self.configure(bg="#f0f0f0")
        
        # Flag to prevent callbacks during initialization
        self._initializing = True
        
        # Variables de estado
        self.current_cup_size = tk.StringVar(value="M")
        self.fill_percentage = tk.DoubleVar(value=75)
        self.current_color = (255, 0, 0)  # Rojo por defecto
        
        # Crear interfaz
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        # Finish initialization
        self._initializing = False
        
        # Actualización inicial
        self._update_calculations()
    
    def _create_widgets(self):
        """Crea todos los widgets de la aplicación."""
        
        # ===== FRAME SUPERIOR: Título =====
        self.header_frame = tk.Frame(self, bg="#2c3e50", height=60)
        self.title_label = tk.Label(
            self.header_frame,
            text="🎨 Calculadora Profesional de Mezclas de Tintas",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        self.subtitle_label = tk.Label(
            self.header_frame,
            text="Calcula las proporciones exactas de colores primarios para tus mezclas",
            font=("Arial", 10),
            fg="#bdc3c7",
            bg="#2c3e50"
        )
        
        # ===== FRAME IZQUIERDO: Controles =====
        self.controls_frame = tk.LabelFrame(
            self, text="Configuración", 
            padx=15, pady=15, font=("Arial", 11, "bold")
        )
        
        # Selector de tamaño de cup
        self.cup_size_frame = tk.Frame(self.controls_frame)
        self.cup_size_label = tk.Label(
            self.cup_size_frame,
            text="Tamaño del Cup:",
            font=("Arial", 11)
        )
        
        self.cup_size_combo = ttk.Combobox(
            self.cup_size_frame,
            textvariable=self.current_cup_size,
            values=get_all_cup_sizes(),
            state="readonly",
            width=8,
            font=("Arial", 11)
        )
        
        # Info del cup
        self.cup_info_label = tk.Label(
            self.cup_size_frame,
            text="",
            font=("Arial", 9),
            fg="#666666"
        )
        
        # Visualizador del cup
        self.cup_visualizer = CupVisualizer(self.controls_frame, width=100, height=120)
        
        # Control de llenado
        self.fill_frame = tk.Frame(self.controls_frame)
        self.fill_label = tk.Label(
            self.fill_frame,
            text="Porcentaje de llenado:",
            font=("Arial", 11)
        )
        
        self.fill_slider = ttk.Scale(
            self.fill_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.fill_percentage,
            length=180
        )
        
        self.fill_value_label = tk.Label(
            self.fill_frame,
            text="75%",
            font=("Arial", 11, "bold"),
            width=5
        )
        
        # Gotas totales
        self.total_drops_label = tk.Label(
            self.controls_frame,
            text="Gotas disponibles: 0",
            font=("Arial", 10),
            fg="#2980b9"
        )
        
        # ===== FRAME CENTRAL: Rueda de color =====
        self.color_frame = tk.LabelFrame(
            self, text="Selección de Color",
            padx=15, pady=15, font=("Arial", 11, "bold")
        )
        
        # Rueda cromática
        self.color_wheel = ColorWheel(
            self.color_frame,
            size=220,
            on_color_change=self._on_color_selected
        )
        
        # Slider de brillo
        self.brightness_frame = tk.Frame(self.color_frame)
        self.brightness_label = tk.Label(
            self.brightness_frame,
            text="Brillo:",
            font=("Arial", 10)
        )
        self.brightness_slider = ttk.Scale(
            self.brightness_frame,
            from_=0.1,
            to=1.0,
            orient=tk.HORIZONTAL,
            length=200,
            command=self._on_brightness_change
        )
        self.brightness_slider.set(1.0)
        
        # Vista previa de colores
        self.color_preview = ColorPreview(self.color_frame, size=70)
        
        # Nombre del color
        self.color_name_label = tk.Label(
            self.color_frame,
            text="Rojo",
            font=("Arial", 12, "bold"),
            fg="#333333"
        )
        
        # ===== FRAME DERECHO: Resultados =====
        self.results_frame = tk.LabelFrame(
            self, text="Resultado de la Mezcla",
            padx=15, pady=15, font=("Arial", 11, "bold")
        )
        
        # Display de gotas
        self.drops_display = DropsDisplay(self.results_frame)
        
        # Instrucciones
        self.instructions_label = tk.Label(
            self.results_frame,
            text="",
            font=("Arial", 9),
            fg="#7f8c8d",
            wraplength=200,
            justify=tk.LEFT
        )
        
        # ===== FOOTER =====
        self.footer_frame = tk.Frame(self, bg="#ecf0f1", height=40)
        self.footer_label = tk.Label(
            self.footer_frame,
            text="💡 Tip: Selecciona un color en la rueda cromática y ajusta el brillo para obtener la mezcla perfecta",
            font=("Arial", 9),
            fg="#7f8c8d",
            bg="#ecf0f1"
        )
        
        # Tooltips
        Tooltip(self.cup_size_combo, 
               "Selecciona el tamaño del cup de tinta\nXL: Grande, S: Pequeño")
        Tooltip(self.fill_slider,
               "Ajusta qué tan lleno quieres el cup\n0% = vacío, 100% = lleno")
        Tooltip(self.brightness_slider,
               "Ajusta el brillo del color\nMenor valor = color más oscuro")
    
    def _setup_layout(self):
        """Configura el layout de la aplicación."""
        
        # Header
        self.header_frame.pack(fill=tk.X)
        self.title_label.pack(pady=(10, 0))
        self.subtitle_label.pack(pady=(0, 10))
        
        # Frame principal de contenido
        self.content_frame = tk.Frame(self, bg="#f0f0f0")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Configurar columnas
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)
        self.content_frame.columnconfigure(2, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Panel izquierdo - Controles
        self.controls_frame.grid(in_=self.content_frame, row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.cup_size_frame.pack(fill=tk.X, pady=(0, 10))
        self.cup_size_label.pack(anchor=tk.W)
        self.cup_size_combo.pack(anchor=tk.W, pady=5)
        self.cup_info_label.pack(anchor=tk.W)
        
        self.cup_visualizer.pack(pady=15)
        
        self.fill_frame.pack(fill=tk.X, pady=10)
        self.fill_label.pack(anchor=tk.W)
        
        fill_controls = tk.Frame(self.fill_frame)
        fill_controls.pack(fill=tk.X)
        self.fill_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.fill_value_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.total_drops_label.pack(anchor=tk.W, pady=(15, 0))
        
        # Panel central - Selector de color
        self.color_frame.grid(in_=self.content_frame, row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.color_wheel.pack(pady=10)
        
        self.brightness_frame.pack(fill=tk.X, pady=10)
        self.brightness_label.pack(side=tk.LEFT)
        self.brightness_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.color_preview.pack(pady=10)
        self.color_name_label.pack()
        
        # Panel derecho - Resultados
        self.results_frame.grid(in_=self.content_frame, row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        self.drops_display.pack(fill=tk.X, pady=10)
        self.instructions_label.pack(fill=tk.X, pady=(20, 0))
        
        # Footer
        self.footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.footer_label.pack(pady=10)
    
    def _bind_events(self):
        """Configura los event handlers."""
        self.current_cup_size.trace_add("write", self._on_cup_size_change)
        self.fill_percentage.trace_add("write", self._on_fill_change)
    
    def _on_cup_size_change(self, *args):
        """Handler para cambio de tamaño de cup."""
        if not self._initializing:
            self._update_calculations()
    
    def _on_fill_change(self, *args):
        """Handler para cambio de porcentaje de llenado."""
        if self._initializing:
            return
        percentage = self.fill_percentage.get()
        self.fill_value_label.configure(text=f"{int(percentage)}%")
        self.cup_visualizer.set_fill_percentage(percentage)
        self._update_calculations()
    
    def _on_color_selected(self, r: int, g: int, b: int):
        """Handler para selección de color en la rueda."""
        self.current_color = (r, g, b)
        if not self._initializing:
            self._update_calculations()
    
    def _on_brightness_change(self, value):
        """Handler para cambio de brillo."""
        if self._initializing:
            return
        brightness = float(value)
        self.color_wheel.set_value(brightness)
    
    def _update_calculations(self):
        """Actualiza todos los cálculos y visualizaciones."""
        cup_size = self.current_cup_size.get()
        fill_pct = self.fill_percentage.get()
        r, g, b = self.current_color
        
        # Actualizar info del cup
        cup_info = get_cup_info(cup_size)
        self.cup_info_label.configure(
            text=f"Vol: {cup_info['volume_ml']:.2f}ml | Máx: {cup_info['max_drops']} gotas"
        )
        
        # Actualizar visualizador del cup
        self.cup_visualizer.set_cup_size(cup_size)
        self.cup_visualizer.set_fill_percentage(fill_pct)
        self.cup_visualizer.set_ink_color(r, g, b)
        
        # Calcular gotas totales
        total_drops = calculate_total_drops(cup_size, fill_pct)
        self.total_drops_label.configure(
            text=f"Gotas disponibles: {total_drops}"
        )
        
        # Calcular mezcla de colores
        color_mix = calculate_color_mix(r, g, b)
        drops = color_mix.to_drops(total_drops)
        
        # Actualizar display de gotas
        self.drops_display.set_drops(
            drops['amarillo'],
            drops['azul'],
            drops['rojo']
        )
        
        # Actualizar vista previa
        self.color_preview.set_target_color(r, g, b)
        self.color_preview.set_result_color(*color_mix.resulting_rgb)
        
        # Actualizar nombre del color
        color_name = get_color_name(r, g, b)
        self.color_name_label.configure(text=color_name)
        
        # Actualizar instrucciones
        self._update_instructions(drops, color_name)
    
    def _update_instructions(self, drops: dict, color_name: str):
        """Actualiza las instrucciones mostradas."""
        instructions = []
        
        if drops['amarillo'] > 0:
            instructions.append(f"• {drops['amarillo']} gota(s) de amarillo")
        if drops['azul'] > 0:
            instructions.append(f"• {drops['azul']} gota(s) de azul")
        if drops['rojo'] > 0:
            instructions.append(f"• {drops['rojo']} gota(s) de rojo")
        
        if instructions:
            text = f"Para obtener {color_name}:\n" + "\n".join(instructions)
        else:
            text = "Selecciona un color y ajusta el llenado"
        
        self.instructions_label.configure(text=text)


def main():
    """Punto de entrada principal de la aplicación."""
    app = TattooInkCalculator()
    
    # Centrar ventana
    app.update_idletasks()
    width = app.winfo_width()
    height = app.winfo_height()
    x = (app.winfo_screenwidth() // 2) - (width // 2)
    y = (app.winfo_screenheight() // 2) - (height // 2)
    app.geometry(f'{width}x{height}+{x}+{y}')
    
    app.mainloop()


if __name__ == "__main__":
    main()
