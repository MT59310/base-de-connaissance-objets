from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware

import io
import time
import zipfile
from PyPDF2 import PdfReader, PdfWriter

app = FastAPI()

# Middleware pour limiter la taille du fichier à 200 Mo
class LimitSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        max_size = 200 * 1024 * 1024  # 200 Mo
        if len(body) > max_size:
            return JSONResponse({"detail": "Fichier trop gros"}, status_code=413)
        return await call_next(request)

app.add_middleware(LimitSizeMiddleware)

@app.post("/split-pdf/")
async def split_pdf(file: UploadFile = File(...)):
    start_time = time.time()

    # Lecture des données brutes
    data = await file.read()
    print("Taille fichier reçue:", len(data), "octets")

    # Recharge le fichier pour PdfReader
    file_stream = io.BytesIO(data)
    pdf_reader = PdfReader(file_stream)
    total_pages = len(pdf_reader.pages)

    # Création du ZIP en mémoire
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        part_number = 1
        pages_per_file = 50  # À ajuster selon ton besoin
        for start in range(0, total_pages, pages_per_file):
            pdf_writer = PdfWriter()
            for page_num in range(start, min(start + pages_per_file, total_pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            part_bytes = io.BytesIO()
            pdf_writer.write(part_bytes)
            part_bytes.seek(0)

            zipf.writestr(f"part_{part_number}.pdf", part_bytes.read())
            part_number += 1

    zip_buffer.seek(0)
    elapsed_time = time.time() - start_time

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=split_parts.zip",
            "X-Processing-Time": f"{elapsed_time:.2f} seconds"
        }
    )
