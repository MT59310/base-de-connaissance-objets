from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import io
import zipfile
from PyPDF2 import PdfReader, PdfWriter

app = FastAPI()

@app.post("/split-pdf/")
async def split_pdf(file: UploadFile = File(...)):
    # Lecture du PDF
    pdf_reader = PdfReader(file.file)
    total_pages = len(pdf_reader.pages)

    # Création du fichier ZIP en mémoire
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        part_number = 1
        pages_per_file = 50  # à ajuster selon la taille
        for start in range(0, total_pages, pages_per_file):
            pdf_writer = PdfWriter()
            for page_num in range(start, min(start + pages_per_file, total_pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            # Sauvegarde en mémoire
            pdf_bytes = io.BytesIO()
            pdf_writer.write(pdf_bytes)
            pdf_bytes.seek(0)

            # Ajout au ZIP
            zipf.writestr(f"part_{part_number}.pdf", pdf_bytes.read())
            part_number += 1

    # Retour du ZIP en téléchargement
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=split_parts.zip"}
    )
