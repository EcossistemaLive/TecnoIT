import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths to prompts and mock data
const PROMPT_DIR = path.join(__dirname, '../../src/config/prompts');
const MOCK_DATA_PATH = path.join(__dirname, 'mock_data.json');
const MOCK_CONTENT_PATH = path.join(__dirname, 'mock_content.json');

// Load Mock Data
const mockData = JSON.parse(fs.readFileSync(MOCK_DATA_PATH, 'utf8'));
const mockContent = JSON.parse(fs.readFileSync(MOCK_CONTENT_PATH, 'utf8'));

// Helper to inject data into template
function injectTemplate(template, data) {
    let result = template;
    for (const key in data) {
        const placeholder = `{{${key}}}`;
        result = result.split(placeholder).join(data[key]);
    }
    return result;
}

async function runHomologationTests() {
    console.log("=== INICIANDO TESTES DE HOMOLOGAÇÃO - BOT JÚLIO ===\n");
    let report = "# Relatório de Homologação - Bot Júlio\n\n";
    report += "Este relatório simula o comportamento do Bot Júlio com dados de teste para validar os prompts e a lógica de RAG.\n\n";

    // 1. Teste de Diagnóstico (Carlos Silva - Fragile)
    console.log("--- TESTE 1: ANALISADOR DE DIAGNÓSTICO ---");
    const diagnosticPromptTemplate = fs.readFileSync(path.join(PROMPT_DIR, 'diagnostic_analyzer.md'), 'utf8');
    const CarlosDiagnostic = mockData.diagnostics.find(d => d.student_id === 'std_001');
    const diagnosticPromptFinal = injectTemplate(diagnosticPromptTemplate, {
        FORM_DATA: JSON.stringify(CarlosDiagnostic.responses, null, 2)
    });

    report += "## 1. Teste de Diagnóstico (Persona: Carlos Silva)\n";
    report += "O objetivo deste teste é validar se o prompt do Analisador de Diagnóstico injeta corretamente os dados do formulário.\n\n";
    report += "### Prompt Montado:\n```markdown\n" + diagnosticPromptFinal + "\n```\n\n";

    // 2. Teste de RAG (Suporte com Contexto)
    console.log("--- TESTE 2: PROTOCOLO RAG (SUPORTE) ---");
    const ragPromptTemplate = fs.readFileSync(path.join(PROMPT_DIR, 'rag_context_prompt.md'), 'utf8');
    const student = mockData.students.find(s => s.id === 'std_001');
    const relevantContent = mockContent.lessons.slice(0, 2).map(l => `[${l.title}]\n${l.content}`).join('\n\n');

    const ragPromptFinal = injectTemplate(ragPromptTemplate, {
        STUDENT_PROFILE: `Nome: ${student.name} | Empresa: ${student.company} | Dores: ${student.pain_points} | Nível: ${student.level}`,
        RETRIEVED_CONTEXT: relevantContent,
        USER_QUERY: "Como posso proteger minha empresa dessa queda de lucro?"
    });

    report += "## 2. Teste de Suporte RAG (Persona: Carlos Silva)\n";
    report += "O objetivo deste teste é validar se o Protocolo RAG injeta corretamente o perfil do aluno e o contexto das aulas.\n\n";
    report += "### Prompt Montado:\n```markdown\n" + ragPromptFinal + "\n```\n\n";

    const reportPath = path.join(__dirname, 'homologation_report.md');
    fs.writeFileSync(reportPath, report);
    console.log(`Relatório gerado em: ${reportPath}`);
    console.log("=== FIM DOS TESTES DE HOMOLOGAÇÃO ===");
}

runHomologationTests().catch(err => console.error(err));
