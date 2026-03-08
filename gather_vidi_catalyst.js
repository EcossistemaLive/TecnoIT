const fs = require('fs');
const path = require('path');

const files = [
    "docs/clickup_status_updated.md",
    "docs/customer_journey_flowchart.md",
    "docs/vidi_orçamento_cupula.md",
    "data/apresentacao_vidi_conceito.html",
    "data/reuniões goianita/Ata_Formal_Cupula_25-02.md",
    "data/reuniões goianita/Ata_Estrategica_Cupula_25-02.md",
    "projects/apresentacao-catalisador/index.html",
    "resources/presentation_cupula.html",
    "projects/proposta_comissionamento_goianita/index.html",
    "projects/naming_vidi/index.html",
    "projects/Cupula-CEO-Presentation/index.html",
    "Reuniões/03-02_Estratégia_de_Negócio_e_Fundamentos_da_Marca_para_uma_Nova_Consultoria_de_Liderança-transcript.txt",
    "resources/Guia da lideranca antifragil.docx.md",
    "resources/ata_reuniao_19_02.html",
    "Reuniões/03-02_Estratégia_de_Negócio_e_Fundamentos_da_Marca_para_uma_Nova_Consultoria_de_Liderança-Resumo.txt",
    "public/brand_reveal.html",
    "docs/cupula_ceo_event_execution_plan.md",
    "docs/organizational_structure.md",
    "data/meeting_analysis_feb_19.html",
    "data/naming_research.txt",
    "docs/pm_suggestions_cupula_ceo.md",
    "data/deep_meeting_analysis_dump.md",
    "data/ata_reuniao_19_02.md",
    "data/Ata_Gerada_07_11.html",
    "data/ata_19_02.md",
    "docs/cupula_ceo_miro_flowchart.mmd",
    "docs/cupula_ceo_epic.md"
];

const basePath = "C:/Users/clebe/OneDrive/Área de Trabalho/ProjetosGit/Gestor de projeto";
const outputPath = "C:/Users/clebe/.gemini/antigravity/brain/d64a20fa-7e08-42cc-81bf-6fef334eb99f/catalyst_vidi_compiled.md";

let outputContent = "# Análise de Arquivos: The Catalyst e ViDi\n\nEste documento compila todos os arquivos e artefatos referenciando os projetos 'The Catalyst' e 'ViDi'.\n\n";

for (const file of files) {
    const fullPath = path.join(basePath, file);
    if (fs.existsSync(fullPath)) {
        const ext = path.extname(fullPath).toLowerCase();

        // Skip large HTMLs if they are just built files. Let's include everything but truncate if too long.
        let content = fs.readFileSync(fullPath, 'utf8');

        if (content.length > 50000) {
            content = content.substring(0, 50000) + "\n\n...[Conteúdo truncado por ser muito longo]...";
        }

        outputContent += `## Arquivo: ${file}\n`;
        if (ext === '.md' || ext === '.txt' || ext === '.mmd') {
            outputContent += "```markdown\n" + content + "\n```\n\n";
        } else if (ext === '.html') {
            outputContent += "```html\n" + content + "\n```\n\n";
        } else {
            outputContent += "```\n" + content + "\n```\n\n";
        }
    } else {
        outputContent += `## Arquivo: ${file}\n*Arquivo não encontrado no caminho especificado.*\n\n`;
    }
}

fs.writeFileSync(outputPath, outputContent);
console.log("Compilation complete: " + outputPath);
