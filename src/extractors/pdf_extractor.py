"""PDF extractor with OCR support for images."""
import io
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from src.utils import logger, settings


class PDFExtractor:
    """Extract text and images from PDF documents with OCR support."""
    
    def __init__(self):
        """Initialize PDF extractor."""
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
        self.logger = logger
    
    def download_pdf(self, url: str, save_path: Optional[Path] = None) -> Path:
        """Download PDF from URL."""
        self.logger.info(f"Downloading PDF from {url}")
        
        headers = {"User-Agent": settings.user_agent}
        response = requests.get(url, headers=headers, timeout=settings.request_timeout)
        response.raise_for_status()
        
        if save_path is None:
            filename = url.split("/")[-1] or "document.pdf"
            save_path = Path(settings.documents_path) / filename
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        self.logger.info(f"PDF saved to {save_path}")
        return save_path
    
    def extract_text_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber (better for tables)."""
        text_content = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    self.logger.debug(f"Extracting text from page {page_num}")
                    text = page.extract_text()
                    if text:
                        text_content.append(f"\n--- Page {page_num} ---\n")
                        text_content.append(text)
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        text_content.append(f"\n--- Tables from Page {page_num} ---\n")
                        for table in tables:
                            text_content.append(self._format_table(table))
        
        except Exception as e:
            self.logger.error(f"Error extracting text with pdfplumber: {e}")
            raise
        
        return "\n".join(text_content)
    
    def extract_images_with_pymupdf(self, pdf_path: Path) -> List[Dict]:
        """Extract images from PDF using PyMuPDF."""
        images = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Save image temporarily
                    image_path = Path(settings.raw_data_path) / f"temp_image_{page_num}_{img_index}.{image_ext}"
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    images.append({
                        "page": page_num + 1,
                        "index": img_index,
                        "path": image_path,
                        "format": image_ext
                    })
                    
                    self.logger.debug(f"Extracted image from page {page_num + 1}, index {img_index}")
                
                except Exception as e:
                    self.logger.warning(f"Error extracting image {img_index} from page {page_num + 1}: {e}")
        
        doc.close()
        return images
    
    def extract_text_from_image(self, image_path: Path) -> str:
        """Extract text from image using OCR."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=settings.ocr_language)
            self.logger.debug(f"Extracted {len(text)} characters from image {image_path.name}")
            return text
        except Exception as e:
            self.logger.warning(f"OCR failed for {image_path}: {e}")
            return ""
    
    def extract_all(self, pdf_path: Path) -> Dict:
        """Extract all content from PDF: text, tables, and images with OCR."""
        self.logger.info(f"Extracting content from {pdf_path}")
        
        # Extract text and tables
        text_content = self.extract_text_with_pdfplumber(pdf_path)
        
        # Extract images
        images = self.extract_images_with_pymupdf(pdf_path)
        
        # Extract text from images using OCR
        image_texts = []
        for img_info in images:
            ocr_text = self.extract_text_from_image(img_info["path"])
            if ocr_text.strip():
                image_texts.append({
                    "page": img_info["page"],
                    "text": ocr_text,
                    "image_path": str(img_info["path"])
                })
        
        # Combine all text
        full_text = text_content
        if image_texts:
            full_text += "\n\n--- Text extracted from images (OCR) ---\n"
            for img_text in image_texts:
                full_text += f"\n--- Image from Page {img_text['page']} ---\n"
                full_text += img_text["text"]
        
        return {
            "text": full_text,
            "images": images,
            "image_texts": image_texts,
            "metadata": {
                "file_path": str(pdf_path),
                "total_pages": len(list(fitz.open(pdf_path))),
                "total_images": len(images),
                "images_with_text": len([img for img in image_texts if img["text"].strip()])
            }
        }
    
    def _format_table(self, table: List[List]) -> str:
        """Format table data as readable text."""
        if not table:
            return ""
        
        formatted_rows = []
        for row in table:
            if row:
                # Clean and join row cells
                cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                formatted_rows.append(" | ".join(cleaned_row))
        
        return "\n".join(formatted_rows)
    
    def process_pdf_url(self, url: str, company_symbol: str = "ETERNAL") -> Dict:
        """Download and extract content from PDF URL."""
        # Download PDF
        pdf_path = self.download_pdf(url)
        
        # Extract all content
        extracted_data = self.extract_all(pdf_path)
        
        # Add metadata
        extracted_data["source_url"] = url
        extracted_data["company_symbol"] = company_symbol
        extracted_data["document_type"] = "quarterly_report"
        
        return extracted_data


def extract_eternal_q2_report() -> Dict:
    """Extract data from Eternal Q2 FY2026 report."""
    url = "https://b.zmtcdn.com/investor-relations/Eternal_Shareholders_Letter_Q2FY26_Results.pdf"
    extractor = PDFExtractor()
    return extractor.process_pdf_url(url, company_symbol="ETERNAL")


if __name__ == "__main__":
    # Test extraction
    result = extract_eternal_q2_report()
    logger.info(f"Extraction complete. Metadata: {result['metadata']}")
    
    # Save extracted text
    output_path = Path(settings.processed_data_path) / "eternal_q2_fy26_extracted.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["text"])
    logger.info(f"Extracted text saved to {output_path}")


