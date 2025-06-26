import re
import json

def parse_questions(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    # Tách từng block câu hỏi dựa vào số thứ tự đầu dòng
    q_blocks = re.split(r'(?m)^\d+\.\s', text)[1:]
    q_nums = [int(m.group(1)) for m in re.finditer(r'(?m)^(\d+)\.\s', text)]
    questions = []
    for idx, block in enumerate(q_blocks):
        lines = block.split('\n')
        qtext_lines = []
        choices = []
        in_choices = False
        for line in lines:
            # Bỏ qua dòng kiểu "Chapter X:"
            if re.match(r'^\s*Chapter\s+\d+[:：]?\s*$', line):
                continue
            # Bỏ qua dòng heading kiểu "56 Chapter 1 ■ Building Blocks"
            if re.match(r'^\s*\d+\s+Chapter\s+\d+', line):
                continue
            # Bỏ qua dòng heading kiểu "Review Questions"
            if re.match(r'^\s*Review Questions', line):
                continue
            m = re.match(r'^([A-Z])\.\s(.+)', line)
            if m:
                in_choices = True
                choices.append({'key': m.group(1), 'text': m.group(2)})
            else:
                if not in_choices:
                    qtext_lines.append(line)
                else:
                    # Nếu đang ở trong phần choices, nối mọi dòng vào choice cuối cùng (kể cả dòng trống)
                    if choices:
                        choices[-1]['text'] += '\n' + line
        # Giữ nguyên định dạng gốc (bao gồm dấu cách đầu dòng, dòng trống)
        qtext = '\n'.join(qtext_lines).strip()
        questions.append({
            'num': q_nums[idx],
            'question': qtext,
            'choices': choices
        })
    return questions

def parse_answers(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    # Xóa các dòng heading appendix/answers
    text = re.sub(r'^\s*\d+\s+Appendix\s+■\s+Answers.*$', '', text, flags=re.MULTILINE)
    # Tách từng block đáp án dựa vào số thứ tự đầu dòng
    a_blocks = re.split(r'(?m)^\d+\.\s', text)[1:]
    a_nums = [int(m.group(1)) for m in re.finditer(r'(?m)^(\d+)\.\s', text)]
    answers = {}
    for idx, block in enumerate(a_blocks):
        # Lấy đáp án (A, B, ...) và phần giải thích
        m = re.match(r'^([A-Z][, A-Z]*)\.\s*(.*)', block, re.DOTALL)
        if m:
            ans = [x.strip() for x in m.group(1).split(',')]
            # Giữ nguyên định dạng giải thích (cả dấu cách đầu dòng)
            expl = m.group(2)
        else:
            ans = []
            expl = block
        answers[a_nums[idx]] = {'answer': ans, 'explanation': expl}
    return answers

def build_json(questions, answers):
    result = []
    for q in questions:
        qnum = q['num']
        ans = answers.get(qnum, {})
        result.append({
            'question': q['question'],
            'choices': q['choices'],
            'answer': ans.get('answer', []),
            'explanation': ans.get('explanation', '')
        })
    return result

def main():
    questions = parse_questions('e:\\upload\\ocp_questions.txt')
    answers = parse_answers('e:\\upload\\ocp_answers.txt')
    data = build_json(questions, answers)
    with open('e:\\upload\\ocp_qa.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
    main()
    main()
