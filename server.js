import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = 3000;

// Serve static files (frontend)
app.use(express.static(__dirname));

// API endpoint to get questions
app.get('/api/questions', (req, res) => {
    const files = ['ocp_qa.json', 'linkedin_qa.json'];
    let allQuestions = [];
    let readCount = 0;
    let hadError = false;

    files.forEach(filename => {
        fs.readFile(path.join(__dirname, 'data', filename), 'utf8', (err, data) => {
            readCount++;
            if (!hadError && err) {
                hadError = true;
                return res.status(500).json({ error: `Cannot read questions from ${filename}` });
            }
            if (!err) {
                try {
                    let questions = JSON.parse(data);
                    allQuestions = allQuestions.concat(questions);
                } catch (e) {
                    if (!hadError) {
                        hadError = true;
                        return res.status(500).json({ error: `Invalid JSON in ${filename}` });
                    }
                }
            }
            if (readCount === files.length && !hadError) {
                res.json(allQuestions);
            }
        });
    });
});

// Fallback to index.html for SPA
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
