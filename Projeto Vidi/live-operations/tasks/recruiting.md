# Task: CV Analysis Pipeline
id: analyze-cv
agent: consultant-support (recruiter mode)
trigger: /rh-analise [cv.pdf]

## Description
Pipeline automatizada de análise de currículo: recebe PDF do CV, analisa com o prompt
Live Recruiter (Protocolo Elite V6.0), extrai o HTML do parecer e publica no GitHub Pages.

## Input
- Arquivo PDF do currículo do candidato
- (Opcional) Arquivo de contexto `.md` com dados da empresa e vaga

## Output
- `Analise_<nome>.md` — Parecer técnico completo (Markdown)
- `Analise_<nome>.html` — Parecer visual HTML (Design System Live V6.0)
- GitHub Pages URL — Página publicada acessível online

## Steps
1. Executar análise do CV com prompt `live-recruiter.md`
2. Gerar parecer com STAR, SWOT, Scorecard e Plano de Imersão
3. Extrair bloco HTML do output
4. Publicar como `index.html` no GitHub Pages
5. Retornar URL da página publicada

## Command (Pipeline Completa)
```bash
node .aios-core/scripts/analyze-cv.js <cv.pdf> --context <contexto.md> --repo <nome-repo>
```

## Command (Etapas Separadas)
```bash
# Etapa 1: Análise
node .aios-core/scripts/run-prompt.js .aios-core/prompts/live-recruiter.md <cv.pdf> --context <contexto.md> -o Analise.md

# Etapa 2: Extrair HTML (manual)
# Copiar bloco ```html``` do .md para um .html

# Etapa 3: Publicar
node .aios-core/scripts/publish-to-pages.js Analise.html --repo <nome-repo>
```
