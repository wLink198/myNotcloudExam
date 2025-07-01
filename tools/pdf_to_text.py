import PyPDF2
import sys
import os

def pdf_to_txt(pdf_path, txt_path):
    reader = PyPDF2.PdfReader(pdf_path)
    with open(txt_path, "w", encoding="utf-8") as out:
        for page in reader.pages:
            text = page.extract_text()
            if text:
                out.write(text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_text.py <input.pdf> [output.txt]")
        sys.exit(1)
    pdf_path = sys.argv[1]
    txt_path = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(pdf_path)[0] + ".txt"
    pdf_to_txt(pdf_path, txt_path)
    print(f"Đã chuyển {pdf_path} thành {txt_path}")
