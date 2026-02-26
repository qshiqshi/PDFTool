import fitz
from pathlib import Path

QUALITY_MAP = {
    "niedrig": 30,
    "mittel": 60,
    "hoch": 85,
}


class PDFCompressor:
    """Compress PDF by reducing image quality and cleaning up."""

    @staticmethod
    def compress(input_path: str, output_path: str,
                 quality: str = "mittel") -> tuple[int, int]:
        jpeg_quality = QUALITY_MAP.get(quality, 60)
        original_size = Path(input_path).stat().st_size

        doc = fitz.open(input_path)

        for page_num in range(doc.page_count):
            page = doc[page_num]
            images = page.get_images(full=True)
            for img in images:
                xref = img[0]
                try:
                    base_image = doc.extract_image(xref)
                    if not base_image:
                        continue
                    img_bytes = base_image["image"]
                    from PIL import Image
                    import io
                    pil_img = Image.open(io.BytesIO(img_bytes))
                    if pil_img.mode in ("RGBA", "P"):
                        pil_img = pil_img.convert("RGB")
                    buf = io.BytesIO()
                    pil_img.save(buf, format="JPEG", quality=jpeg_quality,
                                 optimize=True)
                    new_bytes = buf.getvalue()
                    doc._deleteObject(xref)
                    page.delete_image(xref)
                    rect = page.get_image_rects(xref)
                    if rect:
                        for r in rect:
                            page.insert_image(r, stream=new_bytes)
                except Exception:
                    continue

        doc.save(output_path, garbage=4, deflate=True, clean=True)
        new_size = Path(output_path).stat().st_size
        doc.close()
        return original_size, new_size

    @staticmethod
    def simple_compress(input_path: str, output_path: str) -> tuple[int, int]:
        """Lightweight compression: garbage collection + deflate only."""
        original_size = Path(input_path).stat().st_size
        doc = fitz.open(input_path)
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        new_size = Path(output_path).stat().st_size
        return original_size, new_size
