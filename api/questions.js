import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default function handler(req, res) {
    if (req.method !== 'GET') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    const files = ['ocp_qa.json', 'linkedin_qa.json'];
    let allQuestions = [];
    let readCount = 0;
    let hadError = false;

    files.forEach(filename => {
        fs.readFile(path.join(__dirname, filename), 'utf8', (err, data) => {
            readCount++;
            if (!hadError && err) {
                hadError = true;
                return res.status(500).json({ error: `Cannot read questions from ${filename}` });
            }
            if (!err) {
                try {
                    let questions = JSON.parse(data);
                    questions = questions.map(q => {
                        if (!q.choices || !q.choices.length) {
                            q.choices = 'ABCDEF'.split('').map(k => ({
                                key: k,
                                text: `Choice ${k}`
                            }));
                        }
                        return q;
                    });
                    allQuestions = allQuestions.concat(questions);
                } catch (e) {
                    if (!hadError) {
                        hadError = true;
                        return res.status(500).json({ error: `Invalid JSON in ${filename}` });
                    }
                }
            }
            if (readCount === files.length && !hadError) {
                res.status(200).json(allQuestions);
            }
        });
    });
}
