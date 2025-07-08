import re
import json

def split_by_chapter(text):
    # Split text into (chapter_num, content) tuples, case-insensitive
    matches = list(re.finditer(r'^\s*chapter\s+(\d+)[:：]?.*$', text, re.MULTILINE | re.IGNORECASE))
    chapters = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        chapter_num = int(m.group(1))
        chapters.append((chapter_num, text[start:end]))
    return chapters

def parse_questions_by_chapter(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    chapters = split_by_chapter(text)
    all_questions = []
    for chapter_num, chapter_text in chapters:
        # Split questions by number (e.g. 1. ...), ignore leading whitespace
        q_blocks = re.split(r'(?m)^\s*\d+\.\s', chapter_text)[1:]
        for block in q_blocks:
            lines = block.split('\n')
            qtext_lines = []
            choices = []
            in_choices = False
            current_choice = None
            for i, line in enumerate(lines):
                # Skip headings
                if re.match(r'^\s*Review Questions', line, re.IGNORECASE):
                    continue
                if re.match(r'^\s*\d+\s+Chapter\s+\d+', line, re.IGNORECASE):
                    continue
                m = re.match(r'^([A-Z])\.\s*(.*)$', line)
                if m:
                    in_choices = True
                    key = m.group(1)
                    text = m.group(2)
                    if text.strip() == '':
                        # Choice label only, content in next line(s)
                        # Look ahead for next non-empty line
                        choice_text = ''
                        for j in range(i+1, len(lines)):
                            next_line = lines[j].strip('\r')
                            if next_line.strip() != '' and not re.match(r'^[A-Z]\.\s*$', next_line):
                                choice_text = next_line
                                break
                        choices.append({'key': key, 'text': choice_text})
                    else:
                        choices.append({'key': key, 'text': text})
                    current_choice = choices[-1]
                else:
                    if not in_choices:
                        qtext_lines.append(line)
                    else:
                        # Append to last choice if not a new choice
                        if current_choice is not None and line.strip() != '':
                            current_choice['text'] += '\n' + line
            qtext = '\n'.join(qtext_lines).strip()
            all_questions.append({
                'chapter': chapter_num,
                'question': qtext,
                'choices': choices
            })
    return all_questions

import re

def parse_answers_by_chapter_V2(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    # Remove appendix/answers headings
    text = re.sub(r'^\s*\d+\s+Appendix\s+■\s+Answers.*$', '', text, flags=re.MULTILINE)
    chapters = split_by_chapter(text)
    all_answers = []
    for chapter_num, chapter_text in chapters:
        # Split by question number, keeping the answer part
        a_blocks = re.split(r'(?m)^\s*\d+\.(?=\s*[A-Z])', chapter_text)[1:]
        for block in a_blocks:
            block = block.strip()
            # Match patterns like "A, B and D. Explanation" or "C and D. Explanation"
            m = re.match(r'^([A-Z][^\.]*)\.\s*(.*)', block, re.DOTALL)
            if m:
                raw_ans = m.group(1)
                # Normalize: replace "and" with "," and split
                raw_ans = raw_ans.replace(' and ', ',')
                ans = [x.strip() for x in raw_ans.split(',') if x.strip()]
                expl = m.group(2).strip()
            else:
                ans = []
                expl = block
            all_answers.append({
                'chapter': chapter_num,
                'answer': ans,
                'explanation': expl
            })

    return all_answers

def parse_answers_by_chapter(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    # Remove appendix/answers headings
    text = re.sub(r'^\s*\d+\s+Appendix\s+■\s+Answers.*$', '', text, flags=re.MULTILINE)
    chapters = split_by_chapter(text)
    all_answers = []
    for chapter_num, chapter_text in chapters:
        a_blocks = re.split(r'(?m)^\s*\d+\.(?=[A-Z])', chapter_text)[1:]
        for block in a_blocks:
            m = re.match(r'^([A-Z][, A-Z]*)\.\s*(.*)', block, re.DOTALL)
            if m:
                ans = [x.strip() for x in m.group(1).split(',')]
                expl = m.group(2)
            else:
                ans = []
                expl = block
            all_answers.append({
                'chapter': chapter_num,
                'answer': ans,
                'explanation': expl
            })
    return all_answers

def build_json_by_chapter(questions, answers):
    from collections import defaultdict
    answer_chap_map = defaultdict(list)
    for a in answers:
        answer_chap_map[a['chapter']].append(a)
    question_chap_map = defaultdict(list)
    for q in questions:
        question_chap_map[q['chapter']].append(q)
    result = []
    idx = 357 # for ocp21
    for chapter in sorted(question_chap_map.keys()):
        qlist = question_chap_map[chapter]
        alist = answer_chap_map.get(chapter, [])
        for q_idx, q in enumerate(qlist):
            a = alist[q_idx] if q_idx < len(alist) else {}
            result.append({
                'id': f'ocp-{idx}',
                'question': q['question'],
                'choices': q['choices'],
                'answer': a.get('answer', []),
                'explanation': a.get('explanation', '')
            })
            idx += 1
    return result

def main():
    questions = parse_questions_by_chapter('E:\\upload\\ocp21_questions.txt')
    answers = parse_answers_by_chapter_V2('E:\\upload\\ocp21_answers.txt')
    data = build_json_by_chapter(questions, answers)
    with open('E:\\upload\\ocp21_qa.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
