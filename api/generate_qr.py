from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from main import crear_vcard, generar_qr, crear_etiqueta
from io import BytesIO
from PIL import Image

app = FastAPI()

@app.post("/generate")
async def generate_qr_endpoint(
    nombre: str = Form(...),
    telefono: str = Form(...),
    correo: str = Form(...),
    empresa: str = Form(...)
):
    # 1. Crear vCard
    vcard = crear_vcard(nombre, telefono, correo, empresa)

    # 2. Generar QR
    qr_img = generar_qr(vcard, size_px=600)

    # 3. Crear etiqueta (usa tu fuente incluida en el repo)
    etiqueta = crear_etiqueta(qr_img, nombre, empresa)

    # 4. Guardar en buffer
    buf = BytesIO()
    etiqueta.save(buf, format="PNG")
    buf.seek(0)

    return FileResponse(buf, media_type="image/png", filename="etiqueta.png")
