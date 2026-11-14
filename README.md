# P-IA-NO
Plataforma de Inteligência Artificial para Arranjos Orquestrais em Piano.

## Estado — Bloco 1.3
Três abas. Seleção e reprodução local continuam disponíveis. Agora é possível salvar áudios e pares nomeados na API, listar e reproduzir os arquivos depois de recarregar a página ou reiniciar o processo.

Armazenamento de desenvolvimento: SQLite e arquivos em `data/`, fora do Git. Até 100 MiB por arquivo, 30 minutos de duração e 1 GiB total de áudio. FFprobe verifica o formato real; conteúdo idêntico é reutilizado. A API recebe bytes por streaming e limpa arquivos parciais em falhas normais. Um envio interrompido pode já ter salvo um dos áudios: a nova tentativa reutiliza conteúdo existente.

**Backup manual disponível em Meus modelos → Baixar backup dos dados.** Guarde o ZIP fora deste ambiente. A restauração é executada pelo agente em pasta nova e verifica hashes, formatos, tamanhos e referências. Sem backup automático nem garantia de preservação se o ZIP não for guardado externamente. Não confundir reiniciar a aplicação com preservar dados após perder o servidor. Não expor publicamente: ainda é uma aplicação de desenvolvimento de usuário único e sem autenticação. Executar com apenas um processo/worker. Nenhum treinamento ou geração musical implementado.

## Execução local pelo agente
Requisitos: FFmpeg/ffprobe disponível no PATH (validação de áudio); Python 3.12 com venv/pip; Node 24 e npm 11; acesso aos registries npm/PyPI na instalação. Nenhuma chave de serviço ou GPU necessária.
1. `bash scripts/setup.sh` instala dependências fixadas e compila a interface.
2. `bash scripts/run_local.sh` inicia API e interface em http://127.0.0.1:8000.
3. `.venv/bin/python -m unittest discover -s tests -v` verifica API.
4. `.venv/bin/python scripts/smoke_http.py` verifica o serviço real e os assets compilados.
5. `.venv/bin/python scripts/test_restart.py` verifica salvar, encerrar o processo e recuperar arquivos após reinício.

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

## Backup e recuperação
Ver [docs/BACKUP.md](docs/BACKUP.md). O ZIP contém dados e áudios, não código/modelos/credenciais. Nenhum arquivo de áudio ou backup é versionado no GitHub. O agente pode restaurar com `scripts/backup.py`; o usuário não precisa executar comandos.
