import re
import sys

def validate_answers_order(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    prev_num = None
    for idx, line in enumerate(lines):
        # Nếu gặp dòng chương, reset lại prev_num
        if re.match(r'^\s*Chapter\s+\d+\s*:', line, re.IGNORECASE):
            prev_num = None
            continue
        match = re.match(r'^\s*(\d+)\.', line)
        if match:
            curr_num = int(match.group(1))
            if prev_num is not None and curr_num <= prev_num:
                print(f"Sai thứ tự tại dòng {idx+1}: {line.strip()}")
            prev_num = curr_num

if __name__ == "__main__":
    in_path = sys.argv[1] if len(sys.argv) > 1 else r"input.txt"
    validate_answers_order(in_path)
