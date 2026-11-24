# Bloco 4.18 — início de sessões pelo backend
24/11/2026.

Implementado GET /api/training/pairs, POST /api/training/jobs e GET /api/training/jobs/{id}. POST recebe pair_id, generations (0–3, inteira; 0 é população inicial) e acknowledge_provisional=true. Retorna 202 com job e session_id. Perfil experimental clean-melody-v1, tolerância 200 ms, 100 candidatos, seed 0. Limites fixos neste incremento. Não há transcrição disparada por esse endpoint.

Registro de análise é operação exclusiva do agente/operador: scripts/register_analyzed_pair.py vincula MIDIs e proveniência a um par de MP3 já cadastrado. Valida MIDI não vazio e tamanho, salva hashes e alinhamento provisório. Endpoint não aceita caminhos de arquivo nem código do cliente. Carregamento confere hashes dos MIDIs e dos áudios originais. Registro incompleto/corrompido não fica elegível. Uma correspondência por hash não atesta qualidade de transcrição/alinhamento.

Execução por BackgroundTasks em thread do servidor de desenvolvimento, um trabalho por vez com trava de arquivo. Estados queued/running/completed/failed/interrupted; completed_generation atualizado após cada geração; erros públicos não expõem caminhos privados. Checkpoints completos, MIDIs e proveniência preservados na sessão. GET detecta tarefa abandonada quando a trava está livre, sem retomada automática. Não é fila durável de nuvem nem suporte a múltiplos servidores; processo encerrado exige ação do operador. Se outro trabalho estiver ativo, detecção de tarefa antiga interrompida fica adiada até a trava liberar. Sem cancelamento, idempotência de POST ou retomada pelo endpoint nesta versão.

Teste ponta a ponta usa notas sintéticas controladas e cadastro de áudio fictício, explicitamente sem alegação musical: cria sessão real por POST, executa evolução e consulta histórico. Outros testes cobrem confirmação ausente, limites, cache alterado, falha, estado interrompido e concorrência. Suíte completa 141 testes passou. Nenhum novo treino real ou renderização realizado.

Tifa real foi cadastrado na biblioteca da aplicação e sua análise do piloto 4.17 vinculada por hashes. GET confirmou pronto: pair_id 6e9888cabe7941cea254492eb6a04250. Evidências de metadados em TRAINING_READY_PAIR.json. Áudios permanecem em armazenamento privado e seus originais em arquivos já preservados; notas não entram no Git. É necessário recuperar cadastro/áudios/análise se o ambiente temporário for perdido. O pacote privado 4.17 contém MIDIs e proveniência para reconstruir a análise, com originais anteriores.

Roses and Wine permanece cadastrado sem análise; não consta como pronto. Capacidade geral training na API health continua false pois fluxo de upload→análise→treinamento ainda não está completo. Novo endpoint é experimental e a interface ainda não tem botão de iniciar.

Próximo bloco 4.19: botão para iniciar sessão dos pares prontos, confirmação de uso experimental, progresso/erro e link para histórico/player. Preservar o cadastro de pares sem análise e explicar o estado, sem simular treinamento.
