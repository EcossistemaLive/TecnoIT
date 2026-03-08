$source = "c:\Users\clebe\OneDrive\Área de Trabalho\ProjetosGit\Gestor de projeto"
$dest = "c:\Users\clebe\OneDrive\Área de Trabalho\ProjetosGit\TecnoIT\mentoria_ibrahim\The_Catalyst_ViDi"

New-Item -ItemType Directory -Force -Path $dest | Out-Null

$folders = @("apresentacao-catalisador", "Brand_Reveal", "Cupula-CEO-Presentation", "apresentacao-19-02", "Meeting_Analysis_Feb_19")
foreach ($f in $folders) {
    if (Test-Path "$source\$f") { Copy-Item -Recurse -Force "$source\$f" "$dest\$f" }
}

$filesRoot = @("presentation_cupula.html", "ata_reuniao_19_02.html", "ata_reuniao_2026-02-16.html", "clickup_status.md", "Apresentacao_Ata_Cupula.html")
foreach ($f in $filesRoot) {
    if (Test-Path "$source\$f") { Copy-Item -Force "$source\$f" "$dest\" }
}

New-Item -ItemType Directory -Force -Path "$dest\docs" | Out-Null
$filesDocs = @("cupula_ceo_epic.md", "cupula_ceo_event_execution_plan.md", "cupula_ceo_miro_flowchart.mmd", "customer_journey_flowchart.md", "organizational_structure.md", "pm_suggestions_cupula_ceo.md")
foreach ($f in $filesDocs) {
    if (Test-Path "$source\docs\$f") { Copy-Item -Force "$source\docs\$f" "$dest\docs\" }
}

New-Item -ItemType Directory -Force -Path "$dest\data" | Out-Null
$filesData = @("apresentacao_19_02.html", "apresentacao_ata_19_02.html", "apresentacao_ata_2026-02-16.html", "apresentacao_vidi_conceito.html", "ata_19_02.md", "ata_reuniao_19_02.md", "ata_reuniao_2026-02-16.md", "deep_meeting_analysis_dump.md", "meeting_analysis_feb_19.html", "transcricao_19_02.txt", "naming_research.txt")
foreach ($f in $filesData) {
    if (Test-Path "$source\data\$f") { Copy-Item -Force "$source\data\$f" "$dest\data\" }
}

New-Item -ItemType Directory -Force -Path "$dest\data\reuniões goianita" | Out-Null
if (Test-Path "$source\data\reuniões goianita\Ata_Estrategica_Cupula_25-02.md") {
    Copy-Item -Force "$source\data\reuniões goianita\Ata_Estrategica_Cupula_25-02.md" "$dest\data\reuniões goianita\"
}
if (Test-Path "$source\data\reuniões goianita\Ata_Formal_Cupula_25-02.md") {
    Copy-Item -Force "$source\data\reuniões goianita\Ata_Formal_Cupula_25-02.md" "$dest\data\reuniões goianita\"
}

Write-Host "Migração concluída com sucesso."
