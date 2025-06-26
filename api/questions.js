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
        const filePath = path.join(__dirname, filename);
        console.log(`[Vercel][questions.js] Reading file: ${filePath}`);
        fs.readFile(filePath, 'utf8', (err, data) => {
            readCount++;
            if (!hadError && err) {
                hadError = true;
                console.error(`[Vercel][questions.js] Error reading ${filename}:`, err);
                return res.status(500).json({ error: `Cannot read questions from ${filename}`, detail: err.message });
            }
            if (!err) {
                try {
                    let questions = JSON.parse(data);
                    console.log(`[Vercel][questions.js] Loaded ${questions.length} questions from ${filename}`);
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
                        console.error(`[Vercel][questions.js] Invalid JSON in ${filename}:`, e);
                        return res.status(500).json({ error: `Invalid JSON in ${filename}`, detail: e.message });
                    }
                }
            }
            if (readCount === files.length && !hadError) {
                console.log(`[Vercel][questions.js] Successfully loaded total ${allQuestions.length} questions`);
                res.status(200).json(allQuestions);
            }
        });
    });
}
