# P-IA-NO
Plataforma de Inteligência Artificial para Arranjos Orquestrais em Piano.

## Estado — Bloco 4.8
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

## Núcleo MIDI (Bloco 2.1)
Leitura de MIDI tipo 0/1, extração de notas com trilha/canal, intensidade, início e duração em ticks/semínimas/segundos. Exportação de MIDI a partir dessa representação. Comparação MIDI disponível na aba Treinamento. O agente pode executar `scripts/inspect_midi.py arquivo.mid --json notas.json --midi copia.mid` para inspecionar e reexportar, sem sobrescrever arquivos existentes. Ver docs/MIDI.md.

## Comparação MIDI (Bloco 2.2)
Avaliador interno com precisão/recall/F1 de alturas/inícios/durações, erros médios e lista de correspondências. CLI operada pelo agente: `scripts/compare_midi.py referencia.mid candidato.mid --output relatorio.json`. Sem avaliação artística ou alinhamento automático. Regras, parâmetros e limites em docs/EVALUATOR.md. Integrado à interface na aba Treinamento.

## Comparador no site
Treinamento → Comparar dois MIDIs: selecionar referência/candidato de até 5 MiB cada, ajustar tolerâncias, comparar e baixar JSON. Envio temporário sem persistência. Alterar arquivo/parâmetro limpa o resultado anterior. MIDI não é áudio: não há player ou geração de piano neste recurso.

## Classes de altura e ritmo (Bloco 2.4)
O comparador exibe distribuição de classes de altura, coincidência temporal dessas classes, correspondência de ataques e padrão relativo dos intervalos. Resultados indefinidos aparecem como não calculados, com motivo. São diagnósticos básicos, não reconhecimento de harmonia funcional ou julgamento artístico.

## Redutor interno (Bloco 3.1)
Primeira redução experimental MIDI para duas mãos, com relatório de decisões e limites simultâneos. Ainda sem áudio gerado ou transcrição de MP3. Consulte [REDUCER.md](docs/REDUCER.md). O fluxo final terá entrada MP3 sem conversão manual pelo usuário.

## Áudio de piano (Bloco 3.2)
Renderizador interno gera WAV/MP3 reais a partir do MIDI reduzido, com FluidSynth e TimGM6mb. Limite inicial de 120 s, sem interface de renderização ou transcrição de áudio. Consulte [RENDERER.md](docs/RENDERER.md).

## Piano experimental no site (Bloco 3.3)
Na aba Arranjar, abaixo do upload de áudio original, a ferramenta experimental aceita MIDI de até 5 MiB/120 s e gera piano com player e downloads MIDI/WAV/MP3/JSON. Resultados temporários, fora da biblioteca e backup. Ainda não transforma MP3 orquestral em piano.

## Prova de viabilidade MP3 (experimento separado)
Basic Pitch/ONNX já transcreveu três MP3s sintéticos em CPU. Foram medidas notas extras e erros de duração; não há validação orquestral real nem integração desse transcritor ao site. Receita e resultados: [experiments/README.md](experiments/README.md). O ambiente da aplicação continua separado e inalterado.

## Preparação de trechos (MP3-2a)
Ferramenta interna recorta MP3/WAV/FLAC automaticamente para testes de até 30 segundos, preservando o original e reutilizando resultados íntegros. O usuário pode fornecer o arquivo inteiro. [Detalhes](docs/AUDIO_CLIPS.md). Ainda sem transcrição de gravação orquestral real ou alteração da interface.

## População inicial de candidatos (4.1)
100 configurações por padrão, tamanho ajustável, IDs e manifesto reproduzíveis, geração MIDI sem renderizar áudio por candidato. Ainda sem seleção/evolução. [Detalhes](docs/POPULATION.md). Prova MP3 aceita pelo usuário como suficiente para prosseguir (melodia 7/10, avaliação humana limitada ao trecho).

## Classificação dos candidatos (4.2)
População pode ser avaliada contra referência MIDI alinhada, com pesos configuráveis, critérios explicados, empates e cache de resultados idênticos. Ainda sem evolução/reprodução ou avaliação artística. [Detalhes](docs/RANKING.md).

## Referência de piano em áudio (diagnóstico 4.2a)
Primeiro par real processado com alinhamento DTW proposto e transcrição do piano-objetivo. Ranking calculado apenas para diagnóstico: correspondência temporal ainda requer confirmação. Nenhum score representa acurácia musical. [Estado e limites](docs/PAIRED_AUDIO.md).

## Primeiro ciclo evolutivo (4.3)
Seleção, recombinação, mutação e diversidade implementadas e testadas em referência simbólica controlada. Operação e limites em [docs/EVOLUTION.md](docs/EVOLUTION.md). O par real de Tifa permanece diagnóstico; não orienta reprodução automaticamente.

## Sessões evolutivas retomáveis (4.4)
Várias gerações com checkpoints atômicos, integridade e retomada determinística no mesmo ambiente. Operação pelo agente em scripts/evolve_session.py; detalhes em docs/EVOLUTION.md. Ainda sem painel evolutivo e sem validação auditiva de melhoria.

## Backup de sessões (4.5)
Exportação ZIP e restauração validada de sessões simbólicas em nova pasta. Inclui entradas MIDI e checkpoints; o agente opera scripts/session_backup.py. Procedimento em docs/SESSION_BACKUP.md. Não é backup automático externo.

## Histórico no painel (4.6)
Treinamento agora lista sessões evolutivas e suas gerações, com pontuações e contagens reais. Consulta somente leitura, atualização manual. Ainda não inicia evolução pelo site.

## Candidatos por geração (4.7)
No histórico, escolha uma geração e expanda um dos 10 primeiros candidatos para consultar critérios, pesos, contribuições e parâmetros. Avaliações salvas; sem novo processamento.

## Recuperação de propostas (4.8)
API/CLI recuperam um candidato e verificam que seu MIDI é idêntico ao avaliado. Fonte e código devem corresponder à sessão. Player dos candidatos será integrado no próximo bloco; não há novo treinamento nesta recuperação.
