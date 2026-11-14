# P-IA-NO
Plataforma de Inteligência Artificial para Arranjos Orquestrais em Piano.

## Estado
Bloco 0.1 — preparação técnica, em 14/11/2026. Ainda não existe aplicação web nem processamento musical implementado. Este repositório contém a estrutura e as decisões para começar sem perder progresso.

## Objetivo
Desenvolver arranjadores com poucos pares orquestra/piano, aprovar versões imutáveis e usá-las em composições inéditas. Abas: Treinamento, Arranjar, Meus modelos. A saída será piano solo; não simples troca de timbres.

## Estrutura
- apps/web: futura interface React/TypeScript.
- services/api: futura API Python/FastAPI.
- services/worker: futuro executor de tarefas musicais.
- packages/music: futuro núcleo simbólico compartilhado.
- configs: configurações e decisões versionadas.
- docs: pesquisa técnica e requisitos permanentes.
- scripts: verificação e recuperação.
- tests: futuros testes funcionais; nenhum teste musical foi executado ainda.

## Preparação e execução
Este checkpoint usa somente a biblioteca padrão do Python 3.12 e Git. Não requer instalação de pacotes.
Verificar a estrutura: `python scripts/check_checkpoint.py`.
Não há comando para iniciar o site nesta versão. Instalação do frontend/API, dependências fixadas e scripts de execução serão entregues no Bloco 0.2. Não instalar todos os modelos de IA antecipadamente.

## Continuidade
Ler PROGRESS.md, ARCHITECTURE.md e TODO.md antes de trabalhar. Executar apenas o próximo bloco autorizado. Não contratar infraestrutura nem ativar recursos tarifados sem autorização expressa.
GitHub é o destino principal; sincronização remota ainda pendente da criação do repositório privado.
Ver docs/RECOVERY.md para recuperar o pacote inicial.
