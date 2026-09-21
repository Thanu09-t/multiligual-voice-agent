import io
import re
import zipfile
import xml.etree.ElementTree as ET


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Decode plain text file with fallback encodings."""
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text from Microsoft Word DOCX files by reading
    word/document.xml directly without external dependencies.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            xml_content = zf.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            # Find all text elements in Word XML namespaces
            paragraphs = []
            for p in tree.iter():
                if p.tag.endswith("}p"):
                    p_text = "".join(node.text for node in p.iter() if node.tag.endswith("}t") and node.text)
                    if p_text.strip():
                        paragraphs.append(p_text.strip())
            return "\n\n".join(paragraphs)
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF files. Uses pypdf if available,
    or falls back to resilient stream object extraction.
    """
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)
        if pages_text:
            return "\n\n".join(pages_text)
    except ImportError:
        pass
    except Exception:
        pass

    # Pure Python PDF stream text extractor fallback
    text_fragments = []
    # Search for text objects BT ... ET
    raw_content = file_bytes.decode("latin-1", errors="ignore")
    matches = re.findall(r"\((.*?)\)\s*Tj", raw_content)
    if matches:
        text_fragments.extend(matches)
    
    # Also find bracketed string sequences
    bracket_matches = re.findall(r"\[(.*?)\]\s*TJ", raw_content)
    for bm in bracket_matches:
        parts = re.findall(r"\((.*?)\)", bm)
        text_fragments.extend(parts)

    if text_fragments:
        return " ".join(text_fragments)
    
    # Fallback to general printable character runs
    words = re.findall(r"[a-zA-Z0-9\s.,;:'\"-]{4,}", raw_content)
    return " ".join(words[:200])


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in ["docx", "doc"]:
        return extract_text_from_docx(file_bytes)
    else:
        return extract_text_from_txt(file_bytes)
