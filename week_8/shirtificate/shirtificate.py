# pip install fpdf2
from fpdf import FPDF

name = input("Name: ").strip()

pdf = FPDF(orientation="P", unit="mm", format="A4")
pdf.add_page()
pdf.set_font("times", style="B", size=45)
pdf.ln(20)
pdf.cell(w=0, text="CS50 Shirtificate", align="C")
pdf.ln(35)
pdf.image("./shirtificate.png", w=pdf.epw)
pdf.set_font_size(25)
pdf.set_text_color(255, 255, 255)
pdf.ln(-130)
pdf.multi_cell(
    w=pdf.epw / 2,
    text=f"{name} took CS50",
    align="C",
    center=True,
)
pdf.output("shirtificate.pdf")
