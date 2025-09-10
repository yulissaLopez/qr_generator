# main.py
import json
import io
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import qrcode
import textwrap

# Fuente incluida en la carpeta del proyecto
FUENTE_PATH = "fonts/OpenSansHebrew-Bold.ttf"  # Coloca el .ttf aquí

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

def crear_etiqueta(qr_img, nombre, empresa, ancho_cm=9.0, alto_cm=5.0, dpi=300,
                    fuente_nombre_px=35, fuente_empresa_px=20, margen_px=3, qr_escala=0.6):

    ancho_px, alto_px = cm_a_px(ancho_cm, dpi), cm_a_px(alto_cm, dpi)
    etiqueta = Image.new("RGB", (ancho_px, alto_px), "white")

    qr_max_alto = int((alto_px - 2 * margen_px) * qr_escala)
    qr_redimensionado = qr_img.resize((qr_max_alto, qr_max_alto), Image.NEAREST)
    qr_x = margen_px
    qr_y = (alto_px - qr_redimensionado.height) // 2
    etiqueta.paste(qr_redimensionado, (qr_x, qr_y))

    draw = ImageDraw.Draw(etiqueta)
    font_nombre = ImageFont.truetype(FUENTE_PATH, fuente_nombre_px)
    font_empresa = ImageFont.truetype(FUENTE_PATH, fuente_empresa_px)

    texto_x = qr_x + qr_redimensionado.width + margen_px
    max_text_width = ancho_px - texto_x - margen_px

    def medir_texto(texto, fuente, max_width, spacing=5):
        lineas_finales = []
        for linea in textwrap.wrap(texto, width=40):
            bbox = draw.textbbox((0,0), linea, font=fuente)
            w = bbox[2]-bbox[0]
            if w > max_width:
                sub_lineas = textwrap.wrap(linea, width=max_width//fuente.size)
                lineas_finales.extend(sub_lineas)
            else:
                lineas_finales.append(linea)
        altura = sum(fuente.size + spacing for _ in lineas_finales)
        return altura, lineas_finales

    alto_nombre, lineas_nombre = medir_texto(nombre, font_nombre, max_text_width)
    alto_empresa, lineas_empresa = medir_texto(empresa, font_empresa, max_text_width)
    alto_total_texto = alto_nombre + 10 + alto_empresa
    texto_y = (alto_px - alto_total_texto) // 2

    y = texto_y
    for linea in lineas_nombre:
        bbox = draw.textbbox((0,0), linea, font=font_nombre)
        w = bbox[2]-bbox[0]
        x_linea = texto_x + (max_text_width - w)//2
        draw.text((x_linea, y), linea, font=font_nombre, fill="black")
        y += font_nombre.size + 5

    y += 10
    for linea in lineas_empresa:
        bbox = draw.textbbox((0,0), linea, font=font_empresa)
        w = bbox[2]-bbox[0]
        x_linea = texto_x + (max_text_width - w)//2
        draw.text((x_linea, y), linea, font=font_empresa, fill="black")
        y += font_empresa.size + 5

    return etiqueta

# --- Función de Cloud Function ---
def generar_etiqueta(request):
    """
    Cloud Function HTTP que recibe JSON con campos:
    { "nombre": "...", "telefono": "...", "correo": "...", "empresa": "..." }
    Devuelve la etiqueta como imagen PNG.
    """
    request_json = request.get_json()
    nombre = request_json.get("nombre")
    telefono = request_json.get("telefono")
    correo = request_json.get("correo")
    empresa = request_json.get("empresa")

    vcard = crear_vcard(nombre, telefono, correo, empresa)
    qr_img = generar_qr(vcard)
    etiqueta = crear_etiqueta(qr_img, nombre, empresa)

    # Guardar en buffer para enviar por HTTP
    buf = io.BytesIO()
    etiqueta.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png", as_attachment=True, download_name=f"{nombre}_etiqueta.png")
