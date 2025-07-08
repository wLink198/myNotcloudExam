import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = 3000;

// Cache object
const questionsCache = {};
const files = [
    { name: 'oca_qa.json', category: 'oca' },
    { name: 'ocp_qa.json', category: 'ocp' },
    { name: 'ocp21_qa.json', category: 'ocp' },
    { name: 'linkedin_qa.json', category: 'linkedin' }
];

// Function to load all questions into cache
function loadQuestionsToCache() {
    files.forEach(file => {
        const filePath = path.join(__dirname, 'data', file.name);
        if (!questionsCache[file.category]) {
            try {
                const data = fs.readFileSync(filePath, 'utf8');
                questionsCache[file.category] = JSON.parse(data);
            } catch (e) {
                questionsCache[file.category] = [];
            }
        }
    });
}

// Initial cache load
loadQuestionsToCache();

// Serve static files (frontend)
app.use(express.static(__dirname));

// Helper: limit questions to max 80
function validateQuestionsLimit(questions) {
    if (!Array.isArray(questions)) return [];
    return questions.slice(0, 80);
}

// API endpoint to get questions (all or by category via query param)
app.get('/api/questions', (req, res) => {
    const category = req.query.category;

    if (!category) {
        // Return all questions from cache
        let allQuestions = [];
        files.forEach(file => {
            allQuestions = allQuestions.concat(questionsCache[file.category] || []);
        });
        return res.json(validateQuestionsLimit(allQuestions));
    }

    if (category && questionsCache[category]) {
        return res.json(validateQuestionsLimit(questionsCache[category]));
    }

    return res.json([]);
});

// Fallback to index.html for SPA
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});