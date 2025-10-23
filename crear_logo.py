"""
Crear logo profesional para TradePro
"""

from PIL import Image, ImageDraw, ImageFont
import os

def crear_logo():
    """Crear logo profesional"""
    
    # Crear directorio
    os.makedirs('assets', exist_ok=True)
    
    # Tamaños
    sizes = [256, 128, 64, 32]
    
    for size in sizes:
        # Crear imagen con gradiente
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Fondo con gradiente (simulado con círculos)
        for i in range(size, 0, -2):
            # Gradiente de azul a verde
            r = int(0 + (0 * i / size))
            g = int(168 - (88 * i / size))
            b = int(255 - (119 * i / size))
            alpha = 255
            
            color = (r, g, b, alpha)
            draw.ellipse([
                (size - i) // 2,
                (size - i) // 2,
                (size + i) // 2,
                (size + i) // 2
            ], fill=color)
        
        # Símbolo en el centro
        font_size = size // 3
        try:
            # Intentar usar fuente del sistema
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Dibujar símbolo
        symbol = "TP"
        bbox = draw.textbbox((0, 0), symbol, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - font_size // 4
        
        # Sombra
        draw.text((x + 2, y + 2), symbol, fill=(0, 0, 0, 100), font=font)
        # Texto principal
        draw.text((x, y), symbol, fill=(255, 255, 255, 255), font=font)
        
        # Guardar
        img.save(f'assets/logo_{size}.png')
        print(f"✅ Logo {size}x{size} creado")
    
    # Crear icono .ico (para Windows)
    try:
        logo_256 = Image.open('assets/logo_256.png')
        logo_256.save('assets/icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
        print("✅ Icono .ico creado")
    except Exception as e:
        print(f"⚠️ No se pudo crear .ico: {e}")
    
    print("\n✅ Todos los logos creados en assets/")

if __name__ == "__main__":
    crear_logo()
