# Registro de Uso de IA (prompts.md)

Projeto: Global Solution 2026.2 - CitizenTech - Bolsão Alerta RJ
Disciplina: Computational Thinking with Python

Integrantes:
- Matheus Henrique Pedersen Guerra - RM 571197
- Heitor Anacleto Araújo - RM 573599
- Marcos Vinicius - RM 571080

## Prompts Utilizados no Desenvolvimento

### 1. Compreensão dos Requisitos e Arquitetura Modular
Prompt: "Global Solution 2026.2 - CitizenTech - Computational Thinking with Python - Atividade: O Cérebro Conectado. Código que a equipe não sabe explicar não pontua. Poderia me explicar por favor?"

Objetivo: Entender os requisitos do enunciado em etapas (conexão e contingência antes da análise) e compreender o funcionamento de cada estrutura exigida (RequestException, ValueError, persistência sem duplicidade e exportação CSV).

### 2. Revisão de Conformidade do main.py
Prompt: "Este é meu código, o que devo fazer para preencher os requisitos de entrega? Poderia mandar o código redigido com os requisitos de entrega?"

Objetivo: Revisar o código inicial da equipe, adicionar docstrings descritivas e type hints em todas as funções, validar os pesos e limites com ValueError, ignorar leituras nulas vindas da API e ajustar o fluxo sequencial do menu interativo.

### 3. Validação do Arquivo de Contingência (backup.json)
Prompt: "No código do backup está dentro dos requisitos?"

Objetivo: Validar a estrutura JSON compatível com a resposta da API do ThingSpeak (channel e feeds com entry_id, created_at, field1 e field2) e ampliar os cenários de teste para cobrir todas as faixas de risco (Normal, Atenção e Crítico) e tendência de agravamento.

### 4. Estruturação da Documentação Técnica (README.md)
Prompt: "Meu README está certo? Depois faço o que para entregar?"

Objetivo: Revisar a formatação Markdown, incluir o passo a passo de instalação e execução, documentar a justificativa técnica dos pesos (0.6 e 0.4) e faixas de corte (40.0 e 70.0), e organizar a estrutura final de pastas para submissão no GitHub.