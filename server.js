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
        try {
            const data = fs.readFileSync(filePath, 'utf8');
            const parsedData = JSON.parse(data);

            if (!questionsCache[file.category]) {
                questionsCache[file.category] = parsedData;
            } else {
                questionsCache[file.category] = questionsCache[file.category].concat(parsedData);
            }
        } catch (e) {
            console.error(`Error loading file ${file.name}:`, e);
            if (!questionsCache[file.category]) {
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
function validateQuestionsLimit(questions, n) {
    if (!Array.isArray(questions)) return [];
    if (n > 80) n = 80;
    n = Math.min(n, questions.length);
    shuffle(questions);
    return questions.slice(0, n);
}

function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
}

// API endpoint to get questions (all or by category via query param)
app.get('/api/questions', (req, res) => {
    const category = req.query.category;
    const num = parseInt(req.query.n) || 10; // Default to 10 if not specified
    if (!category) {
        // Return all questions from cache
        let allQuestions = [];
        files.forEach(file => {
            allQuestions = allQuestions.concat(questionsCache[file.category] || []);
        });
        return res.json(validateQuestionsLimit(allQuestions, num));
    }

    if (category && questionsCache[category]) {
        return res.json(validateQuestionsLimit(questionsCache[category], num));
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