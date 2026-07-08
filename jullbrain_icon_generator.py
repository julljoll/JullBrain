import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Se requiere la librería 'Pillow'. Instálala con 'pip install Pillow'.")
    sys.exit(1)

def generate_icon(output_dir):
    # Tamaño del lienzo (512x512 para alta definición y bordes suaves)
    size = 512
    # Crear imagen transparente
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Color de fondo amarillo: #FECF06 (254, 207, 6)
    yellow_color = (254, 207, 6, 255)
    # Dibujar círculo amarillo con un pequeño margen para evitar cortes
    margin = 8
    draw.ellipse([margin, margin, size - 1 - margin, size - 1 - margin], fill=yellow_color)

    # Color del texto: #252525 (37, 37, 37)
    text_color = (37, 37, 37, 255)
    text = "JullBrain"

    # Intentar cargar Arial Bold, sino retroceder a la por defecto
    font_path = "arialbd.ttf"
    font_size = 75
    
    font = None
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        # Rutas comunes en Windows
        win_font = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts", "arialbd.ttf")
        if os.path.exists(win_font):
            try:
                font = ImageFont.truetype(win_font, font_size)
            except IOError:
                pass
                
    if font is None:
        font = ImageFont.load_default()
        print("[AVISO] No se pudo cargar Arial Bold. Se usará la fuente predeterminada.")

    # Calcular dimensiones del texto para centrarlo
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        # Calcular coordenadas iniciales
        text_x = (size - text_w) / 2 - bbox[0]
        text_y = (size - text_h) / 2 - bbox[1]
    else:
        # Retroceso para versiones antiguas de Pillow
        text_w, text_h = draw.textsize(text, font=font)
        text_x = (size - text_w) / 2
        text_y = (size - text_h) / 2

    # Ajustar un poco la y para compensar el centrado óptico
    text_y -= 4

    # Dibujar el texto
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    # Asegurar que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    png_path = os.path.join(output_dir, "jullbrain.png")
    ico_path = os.path.join(output_dir, "jullbrain.ico")

    # Guardar PNG
    image.save(png_path, "PNG")
    print(f"[OK] Icono PNG creado en: {png_path}")

    # Guardar ICO con múltiples tamaños (estándar de Windows para que se vea nítido en escritorio y barra de tareas)
    image.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"[OK] Icono ICO creado en: {ico_path}")

if __name__ == "__main__":
    dest_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_icon(dest_dir)
