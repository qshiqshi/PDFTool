import fitz
from pathlib import Path


class PDFSplitter:
    """Split PDF files into parts."""

    @staticmethod
    def split_all_pages(input_path: str, output_dir: str) -> list[str]:
        doc = fitz.open(input_path)
        stem = Path(input_path).stem
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        files = []
        for i in range(doc.page_count):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
            path = str(out / f"{stem}_Seite_{i + 1}.pdf")
            new_doc.save(path, garbage=4, deflate=True)
            new_doc.close()
            files.append(path)
        doc.close()
        return files

    @staticmethod
    def split_at_ranges(input_path: str, output_dir: str,
                        ranges: list[tuple[int, int]]) -> list[str]:
        """Split at given page ranges (1-based, inclusive)."""
        doc = fitz.open(input_path)
        stem = Path(input_path).stem
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        files = []
        for idx, (start, end) in enumerate(ranges, 1):
            s = max(0, start - 1)
            e = min(doc.page_count - 1, end - 1)
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=s, to_page=e)
            path = str(out / f"{stem}_Teil_{idx}.pdf")
            new_doc.save(path, garbage=4, deflate=True)
            new_doc.close()
            files.append(path)
        doc.close()
        return files

    @staticmethod
    def extract_range(input_path: str, output_path: str,
                      start: int, end: int):
        """Extract page range (1-based, inclusive)."""
        doc = fitz.open(input_path)
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start - 1, to_page=end - 1)
        new_doc.save(output_path, garbage=4, deflate=True)
        new_doc.close()
        doc.close()
