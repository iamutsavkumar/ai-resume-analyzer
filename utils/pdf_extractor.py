import io

def extract_text_from_pdf(uploaded_file) -> str:
    try:
        import fitz  # PyMuPDF

        # Read file ONCE
        pdf_bytes = uploaded_file.read()

        # Reset pointer for reuse
        uploaded_file.seek(0)

        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        extracted_text = []

        for page in pdf_document:
            extracted_text.append(page.get_text("text"))

        pdf_document.close()

        full_text = "\n".join(extracted_text).strip()

        # If PyMuPDF worked → return
        if full_text:
            return full_text

    except Exception as e:
        print(f"[pdf_extractor] PyMuPDF failed: {e}")

    # Fallback using pdfplumber
    try:
        import pdfplumber

        uploaded_file.seek(0)  # RESET again
        pdf_bytes = uploaded_file.read()

        text_parts = []

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        return "\n".join(text_parts).strip()

    except Exception as e:
        print(f"[pdf_extractor] Fallback failed: {e}")
        return ""