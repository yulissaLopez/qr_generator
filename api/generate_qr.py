from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
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
    # 1. Crear vCard
    vcard = crear_vcard(nombre, telefono, correo, empresa)

    # 2. Generar QR
    qr_img = generar_qr(vcard, size_px=600)

    # 3. Crear etiqueta
    etiqueta = crear_etiqueta(qr_img, nombre, empresa)

    # 4. Convertir PIL.Image a PDF usando FPDF
    buf_img = BytesIO()
    etiqueta.save(buf_img, format="PNG")
    buf_img.seek(0)

    pdf = FPDF(unit="pt", format=[etiqueta.width, etiqueta.height])
    pdf.add_page()
    pdf.image(buf_img, 0, 0, etiqueta.width, etiqueta.height)
    
    buf_pdf = BytesIO()
    pdf.output(buf_pdf)
    buf_pdf.seek(0)

    return StreamingResponse(buf_pdf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=etiqueta.pdf"})
