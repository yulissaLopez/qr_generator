# main.py
import json
import io
from PIL import Image, ImageDraw, ImageFont
import qrcode
import textwrap

# Fuente incluida en la carpeta del proyecto
FUENTE_PATH = "fonts/OpenSansHebrew-Bold.tff"  # Coloca el .ttf aquí

# --- Funciones auxiliares ---
def cm_a_px(cm: float, dpi: int = 300) -> int:
    return int(round(cm / 2.54 * dpi))

def crear_vcard(nombre, telefono, correo, empresa):
    nombre = str(nombre)
    telefono = str(telefono)
    correo = str(correo)
    empresa = str(empresa)
    vcard = "BEGIN:VCARD\nVERSION:3.0\n"
    vcard += f"N:{nombre}\nFN:{nombre}\n"
    if telefono.strip() and telefono.lower() != "nan":
        vcard += f"TEL:{telefono}\n"
    if correo.strip() and correo.lower() != "nan":
        vcard += f"EMAIL:{correo}\n"
    if empresa.strip() and empresa.lower() != "nan":
        vcard += f"ORG:{empresa}\n"
    vcard += "END:VCARD"
    return vcard

def generar_qr(contenido, size_px=600, border_modules=4, ec_level="M"):
    ec_map = {"L": qrcode.constants.ERROR_CORRECT_L,
              "M": qrcode.constants.ERROR_CORRECT_M,
              "Q": qrcode.constants.ERROR_CORRECT_Q,
              "H": qrcode.constants.ERROR_CORRECT_H}
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_map.get(ec_level.upper(), qrcode.constants.ERROR_CORRECT_M),
        box_size=10,
        border=border_modules
    )
    qr.add_data(contenido)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size_px, size_px), resample=Image.NEAREST)
    return img

def crear_etiqueta(qr_img: Image.Image, nombre: str, empresa: str, ancho_cm: float = 9.0, alto_cm: float = 12.0, dpi: int = 300, fuente_path: str = FUENTE_PATH, 
                   fuente_nombre_px: int = 28, fuente_empresa_px: int = 22, margen_px: int = 10, qr_escala: float = 0.5) -> Image.Image:
    """
    Crea una etiqueta con el QR en la parte superior
    y el nombre + empresa centrados debajo.
    """
    def cm_a_px(cm, dpi):
        return int(cm * dpi / 2.54)

    # --- Crear lienzo ---
    ancho_px, alto_px = cm_a_px(ancho_cm, dpi), cm_a_px(alto_cm, dpi)
    etiqueta = Image.new("RGB", (ancho_px, alto_px), "white")

    # --- Colocar QR centrado arriba ---
    qr_max_ancho = int(ancho_px * qr_escala)
    qr_redimensionado = qr_img.resize((qr_max_ancho, qr_max_ancho), Image.NEAREST)
    qr_x = (ancho_px - qr_redimensionado.width) // 2
    qr_y = margen_px
    etiqueta.paste(qr_redimensionado, (qr_x, qr_y))

    # --- Preparar texto ---
    draw = ImageDraw.Draw(etiqueta)
    font_nombre = ImageFont.truetype(fuente_path, fuente_nombre_px)
    font_empresa = ImageFont.truetype(fuente_path, fuente_empresa_px)
    max_text_width = ancho_px - 2 * margen_px

    # Función para dividir texto si se pasa del ancho
    def wrap_text(texto, fuente, max_width):
        lineas = []
        for linea in textwrap.wrap(texto, width=15):
            w = draw.textbbox((0, 0), linea, font=fuente)[2]
            if w > max_width:
                sub_lineas = textwrap.wrap(linea, width=max_width // fuente.size)
                lineas.extend(sub_lineas)
            else:
                lineas.append(linea)
        return lineas

    lineas_nombre = wrap_text(nombre, font_nombre, max_text_width)
    lineas_empresa = wrap_text(empresa, font_empresa, max_text_width)

    # --- Calcular posición de texto debajo del QR ---
    texto_y = qr_y + qr_redimensionado.height + 0 # espacio entre QR y texto

    # Dibujar nombre
    y = texto_y
    for linea in lineas_nombre:
        w = draw.textbbox((0,0), linea, font=font_nombre)[2]
        x = (ancho_px - w) // 2
        draw.text((x, y), linea, font=font_nombre, fill="black")
        y += font_nombre.size + 5

    # Espacio entre nombre y empresa
    y += 5
    for linea in lineas_empresa:
        w = draw.textbbox((0,0), linea, font=font_empresa)[2]
        x = (ancho_px - w) // 2
        draw.text((x, y), linea, font=font_empresa, fill="black")
        y += font_empresa.size + 5

    return etiqueta

# nombre = "Yulissa Lopez"
# empresa = "Empresa de Ejemplo"
# correo = "juan.perez@ejemplo.com"
# telefono = "+57 300 123 4567"

# data_qr = f"Nombre: {nombre}\nEmpresa: {empresa}\nCorreo: {correo}\nTeléfono: {telefono}"
# v = crear_vcard(nombre, empresa, correo, telefono)
# qr = generar_qr(v)
# etiqueta = crear_etiqueta(qr, nombre, empresa, ancho_cm=6, alto_cm=5, fuente_nombre_px= 50,
#         fuente_empresa_px= 33)

# etiqueta.show()
# etiqueta.save("etiqueta_prueba.png")

import os
print(os.getcwd())  # te dice la carpeta donde está corriendo Render
print(os.path.exists(FUENTE_PATH))  # True si encuentra la fuente
