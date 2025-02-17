import json
from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        # Header on every page with the main title centered
        self.set_font('DejaVu', 'B', 14)  # Smaller header font size
        self.cell(0, 10, 'Exercise snacking Study', border=False, ln=1, align='C')
        self.ln(3)
        
    def chapter_title(self, title):
        # Title of each section
        self.set_font('DejaVu', 'B', 12)  # Slightly smaller than before
        self.multi_cell(0, 10, title)
        self.ln(2)

    def chapter_body(self, body):
        # Abstract text with smaller font size to fit more content on a page
        self.set_font('DejaVu', '', 10)
        self.multi_cell(0, 7, body)
        self.ln(3)

def main():
    input_file = "abstracts_gpu.json"
    output_file = "Exercise_snacking_Study.pdf"
    
    # Load JSON data
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Create PDF object and add a Unicode font
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Add the Unicode font (ensure the TTF file is in the same directory)
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("DejaVuSans.ttf not found. Please download it and place it in the script directory.")
    
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.add_font("DejaVu", "B", font_path, uni=True)
    
    # Cover page
    pdf.add_page()
    pdf.set_font("DejaVu", 'B', 20)  # Cover page title larger if needed
    pdf.cell(0, 20, "Exercise snacking Study", ln=True, align="C")
    pdf.ln(10)
    
    # Add a page for each entry in JSON
    for entry in data:
        title = entry.get("title", "No Title")
        abstract = entry.get("abstract", "No abstract available.")
        
        pdf.add_page()
        pdf.chapter_title(title)
        pdf.chapter_body(abstract)
    
    # Save the PDF to file
    pdf.output(output_file)
    print(f"PDF saved as {output_file}")

if __name__ == "__main__":
    main()
