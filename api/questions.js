import fs from 'fs';
import path from 'path';

const files = [
    { name: 'oca_qa.json', category: 'oca' },
    { name: 'ocp_qa.json', category: 'ocp' },
    { name: 'linkedin_qa.json', category: 'linkedin' }
];

// Simple in-memory cache (per Vercel instance)
const questionsCache = {};

// Helper: limit questions to max 80
function validateQuestionsLimit(questions) {
    if (!Array.isArray(questions)) return [];
    return questions.slice(0, 80);
}

// Load questions for a category (sync, for simplicity)
function loadQuestions(category) {
    const file = files.find(f => f.category === category);
    if (!file) return [];
    if (questionsCache[category]) return questionsCache[category];
    try {
        const filePath = path.join(process.cwd(), 'data', file.name);
        const data = fs.readFileSync(filePath, 'utf8');
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
        questionsCache[category] = questions;
        return questions;
    } catch {
        questionsCache[category] = [];
        return [];
    }
}

// Load all questions (all categories)
function loadAllQuestions() {
    let all = [];
    files.forEach(f => {
        all = all.concat(loadQuestions(f.category));
    });
    return all;
}

export default function handler(req, res) {
    if (req.method !== 'GET') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }

    // Lấy category từ path hoặc query (?category=...)
    let category = req.query.category;

    if (category && files.some(f => f.category === category)) {
        const questions = loadQuestions(category);
        return res.status(200).json(validateQuestionsLimit(questions));
    }
    // Default: return all
    const allQuestions = loadAllQuestions();
    res.status(200).json(validateQuestionsLimit(allQuestions));
}
