from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from main import crear_vcard, generar_qr, crear_etiqueta
from io import BytesIO
from fpdf import FPDF

app = FastAPI()

@app.post("/generate")
async def generate_qr_pdf(
    nombre: str = Form(...),
    telefono: str = Form(...),
    correo: str = Form(...),
    empresa: str = Form(...)
):
    imagenes = []

    # 1. Crear vCard
    vcard = crear_vcard(nombre, telefono, correo, empresa)

    # 2. Generar QR
    qr_img = generar_qr(vcard, size_px=600)

    # 3. Crear etiqueta
    etiqueta = crear_etiqueta(qr_img, nombre, empresa)
    imagenes.append(etiqueta)

    
    buf = BytesIO()
    imagenes[0].save(
        buf,
        format="PDF",
        save_all=True,
        append_images=imagenes[1:],
        resolution=300
    )
    buf.seek(0)

    return FileResponse(buf, media_type="application/pdf", filename=f"{nombre}_QR.pdf")