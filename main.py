import time  # <-- on ajoute cette importation

@app.post("/split-pdf/")
async def split_pdf(file: UploadFile = File(...)):
    start_time = time.time()  # <-- début du chrono

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

    elapsed_time = time.time() - start_time  # <-- fin du chrono

    # On retourne aussi le temps de traitement dans l’en-tête HTTP
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=split_parts.zip",
            "X-Processing-Time": f"{elapsed_time:.2f} seconds"
        }
    )
