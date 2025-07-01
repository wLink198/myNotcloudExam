import re
import sys
import os

def remove_chapter_sentences(input_path, output_path):
    # Pattern: số + "Chapter" + số + (có thể có dấu - hoặc ký tự bất kỳ sau số chương)
    chapter_pattern = re.compile(r'(\s*\d+\s+Chapter\s+\d+(\s*[-–—\.])?.*)$', re.IGNORECASE)
    # Không remove dòng bắt đầu bằng "Chapter <số>:":
    chapter_colon_pattern = re.compile(r'^\s*Chapter\s+\d+\s*:', re.IGNORECASE)
    ind_pattern = re.compile(r'^c\d{2}\.indd.*Page\s+\d+', re.IGNORECASE)

    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            stripped = line.strip()
            if chapter_colon_pattern.match(stripped):
                outfile.write(line)
                continue
            # Remove chapter pattern at any position, keep the rest
            match = chapter_pattern.search(line)
            if match:
                # Remove the matched pattern, keep the rest (e.g. leading '}')
                new_line = line[:match.start()].rstrip()
                if new_line:
                    outfile.write(new_line + '\n')
                continue
            if ind_pattern.match(stripped):
                continue
            outfile.write(line)

def main():
    if len(sys.argv) < 2:
        print("Usage: python text_formatter.py <input.txt> [output.txt]")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(input_path)[0] + "_out.txt"
    remove_chapter_sentences(input_path, output_path)
    print("Đã xử lý xong.")

if __name__ == "__main__":
    main()
