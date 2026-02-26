import fitz


class PDFMerger:
    """Merge multiple PDF files into one."""

    def __init__(self):
        self.files: list[str] = []

    def add_file(self, path: str):
        self.files.append(path)

    def remove_file(self, index: int):
        if 0 <= index < len(self.files):
            self.files.pop(index)

    def move_file(self, from_idx: int, to_idx: int):
        if 0 <= from_idx < len(self.files) and 0 <= to_idx < len(self.files):
            item = self.files.pop(from_idx)
            self.files.insert(to_idx, item)

    def clear(self):
        self.files.clear()

    def merge(self, output_path: str) -> int:
        if len(self.files) < 2:
            raise ValueError("Mindestens 2 PDFs zum Zusammenfuegen noetig")
        result = fitz.open()
        total_pages = 0
        for path in self.files:
            doc = fitz.open(path)
            result.insert_pdf(doc)
            total_pages += doc.page_count
            doc.close()
        result.save(output_path, garbage=4, deflate=True)
        result.close()
        return total_pages
