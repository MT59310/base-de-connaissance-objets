from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os
import math
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import shutil

app = FastAPI()

@app.post("/split-pdf/")
async def split_pdf(file: UploadFile = File(...)):
    # Créer un dossier temporaire
    output_dir = tempfile.mkdtemp()

    # Sauvegarder le PDF reçu
    input_path = os.path.join(output_dir, file.filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Lire le PDF
    reader = PdfReader(input_path)
    total_size = os.path.getsize(input_path)

    # Nombre de pages par bloc pour environ 10 Mo
    pages_per_chunk = max(1, math.floor(len(reader.pages) / (total_size / (10 * 1024 * 1024))))

    chunk_paths = []
    for start in range(0, len(reader.pages), pages_per_chunk):
        writer = PdfWriter()
        for page in range(start, min(start + pages_per_chunk, len(reader.pages))):
            writer.add_page(reader.pages[page])

        chunk_filename = f"{os.path.splitext(file.filename)[0]}_part_{(start // pages_per_chunk) + 1}.pdf"
        chunk_path = os.path.join(output_dir, chunk_filename)
        with open(chunk_path, "wb") as output_pdf:
            writer.write(output_pdf)

        chunk_paths.append(chunk_path)

    return {"files": chunk_paths}

