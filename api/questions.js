import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default function handler(req, res) {
    if (req.method !== 'GET') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    fs.readFile(path.join(__dirname, '..', 'ocp_qa.json'), 'utf8', (err, data) => {
        if (err) return res.status(500).json({ error: 'Cannot read questions' });
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
        res.status(200).json(questions);
    });
}
