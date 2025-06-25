import fitz, os

class PDFProcessor:
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir

    def convert_to_images(self, pdf_path, base_name):
        doc = fitz.open(pdf_path)
        imgs = []
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=200)
            img_path = os.path.join(self.temp_dir, f"{base_name}_page_{i}.png")
            pix.save(img_path)
            imgs.append(img_path)
        return imgs
