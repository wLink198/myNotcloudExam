import re
from PyPDF2 import PdfReader

def extract_review_questions(pdf_path, output_txt_path):
    review_sections = []
    collecting = False
    buffer = []
    chapter_pattern = re.compile(r"^Chapter\s+\d+", re.IGNORECASE)
    review_start_pattern = re.compile(
        r"^The answers to the chapter review questions can be found in the Appendix.", re.IGNORECASE
    )

    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue
        lines = text.splitlines()
        skip_next = False
        for idx, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
            # Nếu gặp dòng "OCP EXAM OBJECTIVES COVERED IN"
            if "OCP EXAM OBJECTIVES COVERED IN" in line:
                # Xóa dòng trước đó trong buffer nếu có
                if buffer:
                    buffer.pop()
                # Kết thúc section hiện tại
                if collecting:
                    review_sections.append('\n'.join(buffer).strip())
                    buffer = []
                    collecting = False
                # Bỏ qua dòng này và dòng trước đó
                skip_next = False  # đã pop ở trên
                continue
            # Không thêm dòng review_start_pattern vào buffer
            if not collecting and review_start_pattern.match(line.strip()):
                collecting = True
                continue
            if collecting:
                # Stop collecting if a new chapter starts
                if chapter_pattern.match(line.strip()):
                    review_sections.append('\n'.join(buffer).strip())
                    buffer = []
                    collecting = False
                    continue
                buffer.append(line)
    # If still collecting at the end, add the last buffer
    if collecting and buffer:
        review_sections.append('\n'.join(buffer).strip())

    with open(output_txt_path, "w", encoding="utf-8") as out:
        for section in review_sections:
            out.write(section)
            out.write("\n\n")

if __name__ == "__main__":
    pdf_path = "e:/upload/OCP-Oracle-Certified-Professional-Java-SE-17-Developer-Study-Guide-Exam-1Z0-829pdf.pdf"
    output_txt_path = "e:/upload/ocp_review_questions.txt"
    extract_review_questions(pdf_path, output_txt_path)
