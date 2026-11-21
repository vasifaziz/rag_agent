import tempfile
import unittest
import zipfile
from pathlib import Path

from chunker import create_chunks
from document_loader import load_docx
from reranker import rerank


_DOCUMENT_XML = """\
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:pPr><w:pStyle w:val="Title"/></w:pPr><w:r><w:t>Process Guide</w:t></w:r></w:p>
    <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Governance</w:t></w:r></w:p>
    <w:p><w:r><w:t>Human approvals are required before publishing.</w:t></w:r></w:p>
    <w:tbl><w:tr><w:tc><w:p><w:r><w:t>Owner</w:t></w:r></w:p></w:tc>
      <w:tc><w:p><w:r><w:t>Operations</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
    <w:sectPr/>
  </w:body>
</w:document>
"""


class DocumentPipelineTests(unittest.TestCase):
    def test_loads_headings_paragraphs_and_tables(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "guide.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", _DOCUMENT_XML)

            sections = load_docx(path)

        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["document_title"], "Process Guide")
        self.assertEqual(sections[0]["section"], "Governance")
        self.assertIn("Human approvals", sections[0]["text"])
        self.assertIn("Owner | Operations", sections[0]["text"])

    def test_chunks_preserve_document_and_section_context(self):
        chunks = create_chunks(
            [{"document_title": "Process Guide", "section": "Governance",
              "text": "approval " * 13}],
            source="guide.docx",
            chunk_size=8,
            overlap=2,
        )

        self.assertEqual(len(chunks), 3)
        self.assertTrue(all("Process Guide - Governance" in c["text"] for c in chunks))
        self.assertTrue(all(c["source"] == "guide.docx" for c in chunks))

    def test_chunk_overlap_must_be_smaller_than_chunk(self):
        with self.assertRaises(ValueError):
            create_chunks([], source="guide.docx", chunk_size=4, overlap=4)

    def test_reranker_prefers_relevant_nonduplicate_sections(self):
        candidates = [
            {"text": "approval workflow human review publishing", "combined_score": 0.9},
            {"text": "approval workflow human review publishing process", "combined_score": 0.88},
            {"text": "monitoring model cost performance optimization", "combined_score": 0.7},
        ]

        results = rerank("approval workflow", candidates, top_k=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["text"], candidates[0]["text"])
        self.assertEqual(results[1]["text"], candidates[2]["text"])


if __name__ == "__main__":
    unittest.main()
