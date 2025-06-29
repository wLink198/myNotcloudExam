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

// API endpoint to get questions (all categories)
app.get('/api/questions', (req, res) => {
    // Return all questions from cache
    let allQuestions = [];
    files.forEach(file => {
        allQuestions = allQuestions.concat(questionsCache[file.category] || []);
    });
    res.json(validateQuestionsLimit(allQuestions));
});

// API endpoint to get questions by category
app.get('/api/questions/:category', (req, res) => {
    const category = req.params.category;
    if (!questionsCache[category]) {
        return res.status(404).json({ error: 'Category not found' });
    }
    res.json(validateQuestionsLimit(questionsCache[category]));
});

// Fallback to index.html for SPA
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});