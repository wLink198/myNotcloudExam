import re
import json

def parse_quiz(md_path):
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()

    questions = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        # Find question header
        q_match = re.match(r'^####\s+Q\d+\.\s*(.*)', line)
        if q_match:
            # Start collecting question text (may include code block)
            question_lines = []
            question_text = q_match.group(1).strip()
            if question_text:
                question_lines.append(question_text)
            i += 1
            # --- FIX: skip blank lines after question header ---
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            # Collect code block(s) and extra question text
            while i < len(lines):
                l = lines[i].rstrip('\n')
                # Stop if we see a choice or explanation
                if l.strip().startswith('- [') or l.strip().startswith('**Reasoning:**') or l.strip().startswith('**Explanation:**'):
                    break
                if l.strip().startswith('```'):
                    code_block = []
                    code_block.append(l)
                    i += 1
                    while i < len(lines):
                        l2 = lines[i].rstrip('\n')
                        code_block.append(l2)
                        if l2.strip().startswith('```'):
                            i += 1
                            break
                        i += 1
                    question_lines.append('\n'.join(code_block))
                elif l.strip() == '':
                    i += 1
                else:
                    question_lines.append(l)
                    i += 1
            # Compose question text
            question_text = '\n'.join(question_lines).strip()

            # Collect choices
            choices = []
            answer_keys = []
            key_ord = ord('A')
            # Skip empty lines before choices
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            # Parse choices (may be multi-line, including code or code block after - [ ] A/B/C/D)
            while i < len(lines):
                choice_line = lines[i].rstrip('\n')
                # Match - [ ] A or - [x] B etc.
                c_match = re.match(r'^-\s*\[( |x)\]\s*([A-D])\s*$', choice_line)
                if c_match:
                    checked = c_match.group(1) == 'x'
                    key = c_match.group(2)
                    i += 1
                    # Collect all lines (including code blocks and blank lines) until next choice or explanation or question
                    text_lines = []
                    while i < len(lines):
                        next_line = lines[i]
                        # Stop if next line is a new choice or explanation or question
                        if re.match(r'^-\s*\[( |x)\]\s*[A-D]\s*$', next_line) \
                            or next_line.strip().startswith('**Reasoning:**') \
                            or next_line.strip().startswith('**Explanation:**') \
                            or next_line.strip().startswith('#### Q'):
                            break
                        text_lines.append(next_line.rstrip('\n'))
                        i += 1
                    text = '\n'.join(text_lines).strip()
                    choices.append({'key': key, 'text': text})
                    if checked:
                        answer_keys.append(key)
                else:
                    # fallback: old style - [ ] <text>
                    c_match2 = re.match(r'^-\s*\[( |x)\]\s*(.*)', choice_line)
                    if c_match2:
                        checked = c_match2.group(1) == 'x'
                        text = c_match2.group(2)
                        choice_lines = [text]
                        i += 1
                        while i < len(lines):
                            next_line = lines[i]
                            if (re.match(r'^-\s*\[( |x)\]', next_line)
                                or next_line.strip().startswith('**Reasoning:**')
                                or next_line.strip().startswith('**Explanation:**')
                                or next_line.strip().startswith('#### Q')):
                                break
                            if next_line.startswith('    ') or next_line.startswith('\t') or next_line.strip().startswith('```'):
                                choice_lines.append(next_line.rstrip('\n'))
                            else:
                                break
                            i += 1
                        text = '\n'.join(choice_lines).strip()
                        key = chr(key_ord)
                        choices.append({'key': key, 'text': text})
                        if checked:
                            answer_keys.append(key)
                        key_ord += 1
                    else:
                        break

            # Collect explanation (lines starting with **Reasoning:**, **Explanation:**, or similar)
            explanation = ""
            # Skip empty lines
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            exp_lines = []
            while i < len(lines):
                exp_line = lines[i].rstrip('\n')
                if exp_line.strip().startswith('**Reasoning:**') or exp_line.strip().startswith('**Explanation:**'):
                    exp_lines.append(exp_line.split(':', 1)[-1].strip())
                    i += 1
                    # Collect following lines until next question or reference or empty line before next question
                    while i < len(lines):
                        next_line = lines[i].rstrip('\n')
                        if (next_line.strip().startswith('#### Q') or 
                            next_line.strip().startswith('---') or 
                            next_line.strip().startswith('[Reference]') or
                            (next_line.strip() == '' and i + 1 < len(lines) and 
                             lines[i + 1].strip().startswith('#### Q'))):
                            break
                        if next_line.strip() != '':
                            exp_lines.append(next_line.strip())
                        i += 1
                    break
                elif exp_line.strip().startswith('[Reference]'):
                    i += 1
                elif exp_line.strip().startswith('#### Q'):
                    break
                elif exp_line.strip() == '':
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith('#### Q'):
                        break
                    i += 1
                else:
                    i += 1
            if exp_lines:
                explanation = ' '.join(exp_lines)
            # If no explanation, leave as empty string

            questions.append({
                "question": question_text,
                "choices": choices,
                "answer": answer_keys,
                "explanation": explanation
            })
        else:
            i += 1

    # Add id and default explanation if missing
    for idx, q in enumerate(questions, 1):
        # Move id to the first field
        qid = f"linkedin-{idx}"
        if not q.get("explanation"):
            q["explanation"] = "Google serach or AI for this shiet bro."
        # Reorder fields: id, question, choices, answer, explanation
        reordered = {
            "id": qid,
            "question": q["question"],
            "choices": q["choices"],
            "answer": q["answer"],
            "explanation": q["explanation"]
        }
        questions[idx-1] = reordered
    return questions

if __name__ == "__main__":
    import sys
    md_path = sys.argv[1] if len(sys.argv) > 1 else r"D:\exam-app\java-quiz.md"
    out_path = sys.argv[2] if len(sys.argv) > 2 else r"linkedin_qa.json"
    data = parse_quiz(md_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(data)} questions to {out_path}")