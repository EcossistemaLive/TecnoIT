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

const sourceBase = "C:/Users/clebe/OneDrive/Área de Trabalho/ProjetosGit/Gestor de projeto";
const targetBase = "C:/Users/clebe/OneDrive/Área de Trabalho/ProjetosGit/TecnoIT/Projeto Vidi/Arquivos_Gestor_De_Projeto";

for (const file of files) {
    const sourcePath = path.join(sourceBase, file);
    const targetPath = path.join(targetBase, file);

    if (fs.existsSync(sourcePath)) {
        fs.mkdirSync(path.dirname(targetPath), { recursive: true });
        fs.copyFileSync(sourcePath, targetPath);
        console.log(`Copiado: ${file}`);
    } else {
        console.log(`Não encontrado: ${file}`);
    }
}
