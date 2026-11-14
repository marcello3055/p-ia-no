# P-IA-NO
Plataforma de Inteligência Artificial para Arranjos Orquestrais em Piano.

## Estado — Bloco 0.2
Interface React/TypeScript e API FastAPI mínimas. A tela consulta de verdade `/api/health`, informa sucesso/erro e permite tentar novamente. Os três ambientes são apresentados como planejados: ainda não existem uploads, treinamento ou geração musical.

## Execução local pelo agente
Requisitos: Python 3.12 com venv/pip; Node 24 e npm 11; acesso aos registries npm/PyPI na instalação. Nenhuma chave de serviço ou GPU necessária.
1. `bash scripts/setup.sh` instala dependências fixadas e compila a interface.
2. `bash scripts/run_local.sh` inicia API e interface em http://127.0.0.1:8000.
3. `.venv/bin/python -m unittest discover -s tests -v` verifica API.
4. `.venv/bin/python scripts/smoke_http.py` verifica o serviço real e os assets compilados.

Desenvolvimento: iniciar a API com o script acima e, em outro terminal, `npm --prefix apps/web run dev`. Vite encaminha `/api` para a API local. Build: `npm --prefix apps/web run build`.
Esses comandos são para o agente; o usuário não precisa executá-los. O endereço local não abre no celular do usuário; hospedagem permanente ainda não configurada.

## Estrutura
- apps/web: interface React, estilos locais, sem fontes/CDNs externos.
- services/api: API e serviço dos arquivos compilados.
- services/worker e packages/music: reservados; sem processamento implementado.
- configs e docs: planejamento e regras versionadas.
- scripts e tests: preparação, execução e verificações.

## Continuidade e custos
Repositório principal privado: https://github.com/marcello3055/p-ia-no
Ler PROGRESS.md, ARCHITECTURE.md e TODO.md. Um bloco por autorização. Componentes gratuitos/open source, sem APIs pagas nem recursos tarifados. GitHub é o serviço de versionamento expressamente escolhido pelo usuário; seu uso não implica que o serviço seja open source. Não usar GitHub Actions para tarefas pesadas ou faturáveis.
Dados e modelos fora do Git. Dependências JavaScript em package-lock.json; Python em requirements.lock com hashes. Nenhum modelo de IA instalado. Sem promessa de GPU ou hospedagem gratuita permanente.
