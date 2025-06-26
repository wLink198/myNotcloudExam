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
    fs.readFile(path.join(__dirname, 'ocp_qa.json'), 'utf8', (err, data) => {
        if (err) return res.status(500).json({ error: 'Cannot read questions' });
        let questions = JSON.parse(data);
        // Add dummy choices if missing (for demo, real app should have choices in JSON)
        questions = questions.map(q => {
            if (!q.choices || !q.choices.length) {
                // Generate choices A-F as placeholders
                q.choices = 'ABCDEF'.split('').map(k => ({
                    key: k,
                    text: `Choice ${k}`
                }));
            }
            return q;
        });
        res.json(questions);
    });
});

// Fallback to index.html for SPA
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
