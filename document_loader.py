import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


_WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_NS = {"w": _WORD_NS}
_WORD_TAG = f"{{{_WORD_NS}}}"


def _paragraph_text(paragraph):
    pieces = []
    for element in paragraph.iter():
        if element.tag == f"{_WORD_TAG}t":
            pieces.append(element.text or "")
        elif element.tag == f"{_WORD_TAG}tab":
            pieces.append(" ")
        elif element.tag in {f"{_WORD_TAG}br", f"{_WORD_TAG}cr"}:
            pieces.append(" ")
    return re.sub(r"\s+", " ", "".join(pieces)).strip()


def _table_text(table):
    rows = []
    for row in table.findall("./w:tr", _NS):
        cells = []
        for cell in row.findall("./w:tc", _NS):
            text = " ".join(
                filter(None, (_paragraph_text(p) for p in cell.findall(".//w:p", _NS)))
            )
            if text:
                cells.append(text)
        if cells:
            rows.append(" | ".join(cells))
    return rows


def load_docx(path):
    """Extract ordered, section-aware text from a Word document."""
    path = Path(path)
    if path.suffix.lower() != ".docx":
        raise ValueError(f"Expected a .docx document: {path.name}")

    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise ValueError(f"Could not read Word document {path.name}: {exc}") from exc

    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise ValueError(f"Invalid Word document XML in {path.name}: {exc}") from exc

    body = root.find("./w:body", _NS)
    if body is None:
        raise ValueError(f"Word document has no body: {path.name}")

    document_title = path.stem
    current_section = document_title
    sections = []
    paragraphs = []

    def save_section():
        text = "\n".join(paragraphs).strip()
        if text:
            sections.append({
                "document_title": document_title,
                "section": current_section,
                "text": text,
            })
        paragraphs.clear()

    for child in body:
        if child.tag == f"{_WORD_TAG}p":
            text = _paragraph_text(child)
            if not text:
                continue
            style = child.find("./w:pPr/w:pStyle", _NS)
            style_name = (
                style.attrib.get(f"{_WORD_TAG}val", "").lower()
                if style is not None
                else ""
            )
            if style_name == "title":
                save_section()
                document_title = text
                current_section = text
            elif style_name.startswith("heading"):
                save_section()
                current_section = text
            else:
                paragraphs.append(text)
        elif child.tag == f"{_WORD_TAG}tbl":
            paragraphs.extend(_table_text(child))

    save_section()
    if not sections:
        raise ValueError(f"No readable text found in {path.name}")
    return sections
