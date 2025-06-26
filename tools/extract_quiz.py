import re
import json

def parse_quiz(md_path):
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()

    questions = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Find question header
        q_match = re.match(r'^####\s+Q\d+\.\s*(.*)', line)
        if q_match:
            question_text = q_match.group(1)
            # If question text is empty, try next line
            if not question_text:
                i += 1
                if i < len(lines):
                    question_text = lines[i].strip()
            
            # Collect choices
            choices = []
            answer_keys = []
            i += 1
            
            # Skip empty lines before choices
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            while i < len(lines):
                choice_line = lines[i].strip()
                # Choices are markdown checkboxes
                c_match = re.match(r'^-\s*\[( |x)\]\s*(.*)', choice_line)
                if c_match:
                    checked = c_match.group(1) == 'x'
                    text = c_match.group(2)
                    key = chr(ord('A') + len(choices))
                    choices.append({'key': key, 'text': text})
                    if checked:
                        answer_keys.append(key)
                    i += 1
                elif choice_line == '':
                    # Empty line, continue to look for explanation or next question
                    i += 1
                    continue
                else:
                    # Not a choice, break to look for explanation
                    break
            
            # Collect explanation (lines starting with **Reasoning:** or **Explanation:** or similar)
            explanation = ""
            while i < len(lines):
                exp_line = lines[i].strip()
                if exp_line.startswith('**Reasoning:**') or exp_line.startswith('**Explanation:**'):
                    explanation = exp_line.split(':', 1)[-1].strip()
                    # Also collect following lines until next question or reference
                    i += 1
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if (next_line.startswith('#### Q') or 
                            next_line.startswith('---') or 
                            next_line.startswith('[Reference]') or
                            (next_line == '' and i + 1 < len(lines) and 
                             lines[i + 1].strip().startswith('#### Q'))):
                            break
                        if next_line:  # Don't add empty lines
                            explanation += ' ' + next_line
                        i += 1
                    break
                elif exp_line.startswith('```'):
                    # Skip code blocks - find the end
                    i += 1
                    while i < len(lines):
                        if lines[i].strip().startswith('```'):
                            i += 1
                            break
                        i += 1
                elif exp_line.startswith('[Reference]'):
                    # Skip reference lines
                    i += 1
                elif exp_line.startswith('#### Q'):
                    # Next question found
                    break
                elif exp_line == '':
                    # Empty line, check if next line is a new question
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith('#### Q'):
                        break
                    i += 1
                else:
                    i += 1
            
            if not explanation:
                explanation = "Go google or AI for the explanation bro."
            
            questions.append({
                "question": question_text,
                "choices": choices,
                "answer": answer_keys,
                "explanation": explanation
            })
        else:
            i += 1
    
    return questions

if __name__ == "__main__":
    import sys
    md_path = sys.argv[1] if len(sys.argv) > 1 else r"D:\exam-app\java-quiz.md"
    out_path = sys.argv[2] if len(sys.argv) > 2 else r"linkedin_qa.json"
    data = parse_quiz(md_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(data)} questions to {out_path}")