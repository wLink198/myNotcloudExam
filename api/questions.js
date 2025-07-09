import fs from 'fs';
import path from 'path';

// Simple in-memory cache (per Vercel instance)
const questionsCache = {};
const files = [
    { name: 'oca_qa.json', category: 'oca' },
    { name: 'ocp_qa.json', category: 'ocp' },
    { name: 'ocp21_qa.json', category: 'ocp' },
    { name: 'linkedin_qa.json', category: 'linkedin' }
];

// Shuffle helper
function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
}

// Limit questions
function validateQuestionsLimit(questions, n) {
    if (!Array.isArray(questions)) return [];
    n = Math.min(n, 80, questions.length);
    shuffle(questions);
    return questions.slice(0, n);
}

// Load questions from file
function loadQuestions(category) {
    const matchedFiles = files.filter(f => f.category === category);
    if (matchedFiles.length === 0) return [];

    let allQuestions = [];

    matchedFiles.forEach(file => {
        try {
            const filePath = path.join(process.cwd(), 'data', file.name);
            const data = fs.readFileSync(filePath, 'utf8');
            const parsedData = JSON.parse(data);
            allQuestions = allQuestions.concat(parsedData);
        } catch (e) {
            console.error(`Error loading file ${file.name}:`, e);
        }
    });

    return allQuestions;
}

// Load all questions
function loadAllQuestions() {
    let all = [];
    files.forEach(file => {
        all = all.concat(loadQuestions(file.category));
    });
    return all;
}

// Vercel API handler
export default function handler(req, res) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const category = req.query.category;
    const num = parseInt(req.query.n) || 10;

    if (!category) {
        const allQuestions = loadAllQuestions();
        return res.status(200).json(validateQuestionsLimit(allQuestions, num));
    }

    if (questionsCache[category] || files.some(f => f.category === category)) {
        const questions = loadQuestions(category);
        return res.status(200).json(validateQuestionsLimit(questions, num));
    }

    return res.status(404).json([]);
}
