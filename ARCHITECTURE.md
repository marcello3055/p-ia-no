# Arquitetura inicial — decisão 001
Data: 14/11/2026. Arquitetura escolhida; implementação pendente.

## Componentes
| Componente | Escolha inicial | Motivo |
|---|---|---|
| Interface | React + TypeScript + Vite, responsiva | Aplicação de três abas sem necessidade inicial de SSR; saída estática hospedável separadamente |
| API | Python 3.12 + FastAPI | Integração com ferramentas musicais; API separada de tarefas demoradas |
| Executor | Processo Python separado | Não bloquear requisições ou manter uma chamada HTTP por todo treinamento |
| Protótipo local | SQLite + diretório de dados fora do Git | Poucas dependências; somente uma instância inicialmente |
| Nuvem durável | PostgreSQL + armazenamento de objetos compatível com S3 | Metadados, tarefas e objetos independentes do ciclo de vida dos servidores |
| Representação | JSON musical versionado + MIDI | JSON preserva confiança, vozes, mãos e proveniência que MIDI não representa bem |
| Renderização | Adaptador FluidSynth + piano SF2 com licença verificada | Renderização offline em CPU; instrumento exato ainda não selecionado |

A interface poderá ser hospedada como site estático. O ambiente Sites usa Workers e não substitui o executor Python de ML. Não colocar modelos musicais, tarefas longas ou arquivos grandes dentro do frontend. Para desenvolvimento, API e worker executam no ambiente disponível; isso não equivale a hospedagem permanente.

## Fluxo planejado
Upload privado → validação → tarefa persistida → análise em cache → representação musical → redução/otimização → avaliação → renderização dos finalistas → arquivos e histórico.
Cada tarefa terá proprietário, estado, progresso, erro, tentativas, cancelamento e checkpoint. O worker deverá adquirir uma tarefa atomicamente, renovar sua posse e permitir retomada após interrupção. Implementar inicialmente uma instância; fila distribuída só quando necessária.

## Cache e representação
Chave de análise: hash do arquivo + versão do analisador + hash dos parâmetros e modelo. Guardar alturas, onsets, durações, compassos/tempos, vozes, confiança e origem. Distinguir tempo musical de segundos de execução; pedal e rubato pertencem também à interpretação.

## Arranjadores e evolução
100 candidatos configuráveis compartilham analisadores; seus genomas contêm parâmetros e estratégias de redução. Começar com seleção, elitismo, mutação e recombinação simples, com diversidade mensurável. Considerar NSGA-II apenas se o baseline justificar.
Currículo: melodia → harmonia/acompanhamento → tocabilidade → expressividade. Guardar métricas separadas, pesos e mínimos obrigatórios. Avaliar simbolicamente; renderizar finalistas. Não apresentar escores como comprovação de qualidade auditiva.

Aprovar cria snapshot imutável com nome, versão, parentesco, parâmetros, seed, código/commit, dependências fixadas, IDs/revisões/hashes de modelos, análises, avaliadores e instrumento. Ajustar cria nova versão. Refinamento de uma música nunca atualiza o aprovado. Reprodutibilidade numérica exige registrar hardware e operações não determinísticas; áudio bit a bit não será prometido sem teste.

## Avaliação e alinhamento
Métricas supervisionadas: notas alinhadas, contorno, ritmo, baixo, harmonia, densidade e restrições pianísticas; referência não é única solução correta. Avaliador autônomo usa representação da orquestra e restrições pianísticas, com incerteza explícita. Sua qualidade precisa ser validada por escuta e repertório reservado.
DTW sobre chroma/representações melódicas é baseline; introduções, repetições e cortes exigem segmentação e correção humana. Alinhamento fraco deve bloquear comparação enganosa.
Divisão treino/validação por composição completa, inclusive versões e trechos relacionados. 5–20 pares calibram parâmetros; não justificam treinar modelo geral do zero nem alegar generalização.

## Persistência, importação e segurança
Arquivos e pesos fora do Git, acesso privado e URLs temporárias. Antes de hospedar uploads: autenticação, isolamento por usuário, limites de tamanho/duração, validação real de formato e processamento com limites de recursos. Importar JSON e formatos permitidos, nunca executar código/pickle de pacote importado; rejeitar caminhos escapando do diretório, arquivos excessivos e hashes inválidos. Respeitar licenças e usar referências externas quando pesos/amostras não puderem ser redistribuídos.

## Custos e implantação
Nenhum serviço contratado. CPU atende estrutura, MIDI e primeiras reduções; desempenho será medido, não estimado como garantia. Para MT3/transcrição pesada, reservar arquitetura para GPU externa sob demanda; aluguel só após benchmark e autorização.
Candidatos de infraestrutura a comparar na implantação: hospedagem estática Sites; API/worker em container Linux com volume persistente; PostgreSQL gerenciado e objetos S3. Provedores e planos ainda não escolhidos; não há promessa de camada gratuita permanente. Antes da contratação, apresentar preço vigente, GPU-hora × duração medida, armazenamento, tráfego e teto autorizado. Suspender tarefas ao atingir limites. Não há acesso ao saldo de créditos do usuário.

## Atualização do Bloco 0.2
Componentes implementados: React/TypeScript/Vite e FastAPI/Uvicorn. Produção local usa a mesma origem HTTP: FastAPI serve o build e /api/health; desenvolvimento usa proxy Vite. Sem necessidade de CORS aberto. Bind somente em loopback: publicação exige etapa posterior de autenticação e infraestrutura.
Regra adicional do usuário: somente ferramentas gratuitas/open source; serviços pagos não serão adotados. Dependências novas exigem verificação de licença antes da adoção. Software livre não garante computação gratuita. Fontes, estilos e scripts da interface são locais.

## Bloco 1.2 — persistência de desenvolvimento
`Store` usa SQLite com foreign keys e arquivos por UUID; nomes originais são metadados. POST /api/audio recebe bytes (application/octet-stream), nome em query, hash SHA-256, limites durante streaming e ffprobe com timeout/protocolo file. GET /api/audio, POST/GET /api/pairs e GET /api/audio/{id}/content (suporta Range para seek). Áudio bruto e DB não entram no Git.
Limites: 100 MiB/arquivo, 30 minutos, 1 GiB de áudio; sem transcrição. Lock asyncio serializa uploads em UM processo; múltiplos workers não suportados. IDs de pares repetidos retornam o registro existente. Dados em PIANO_DATA_DIR ou data/ por padrão. Sem autenticação, delete, backup ou isolamento multiusuário; bind local e preview de desenvolvimento somente. Falhas normais limpam partes; encerramento abrupto pode deixar órfãos que contam para quota. SQLite e filesystem não formam uma transação atômica conjunta; recuperação/backup é o próximo incremento.

## Bloco 1.3 — backup portátil
ZIP de dados com manifesto JSON versionado, SHA-256 e arquivos permitidos; SQLite é reconstruído em pasta nova, nunca importado como banco executável. Endpoint de exportação e ferramenta CLI de restauração, com validação e limpeza em falha. Biblioteca ativa não é substituída automaticamente. Backup manual baixado para dispositivo externo é a opção inicial sem serviço pago; automação/durabilidade em nuvem permanece pendente. Ver docs/BACKUP.md.

## Bloco 2.1 — núcleo simbólico
Módulo Python independente de API/frontend: Score/Note/Event, tempo PPQN e conversão em segundos pelo mapa global. Eventos de controle preservados; roles/mãos não inferidos. MIDI exportado é reconstruído a partir da representação; testes comprovam que edição simbólica altera a saída. Padrões/limites em docs/MIDI.md. Próximo componente: métricas iniciais, sem chamar essas métricas de qualidade artística.

## Bloco 2.2 — avaliador inicial
Comparação simbólica independente da API. Pareamento um a um por altura/início, métricas separadas com cobertura, índices e configuração versionada. Unidades musicais ou segundos configuráveis; sem alinhamento implícito. Métricas não representam qualidade artística. Detalhes em docs/EVALUATOR.md.

## Bloco 2.3 — comparação pela interface
Painel React MidiCompare e endpoint efêmero /api/midi/compare; upload binário limitado, sem dependência multipart ou persistência. Comparação em thread, um pedido por processo. Resultados anteriores invalidados ao mudar seleção/configuração. Download JSON no cliente. Não equivale a treinamento nem áudio gerado.

## Bloco 2.4 — diagnósticos complementares
patterns.py opera sobre notas normalizadas pelo avaliador. Classes de altura por duração e Jaccard temporal via varredura de eventos (sem matriz de frames), ataques únicos e intervalos normalizados. Retorna dados explicáveis e null quando não há suporte suficiente. Integrado à API, JSON e painel por evaluator_version 0.2.0.

## Bloco 3.1 — redução simbólica
packages/music/reduce.py implementa heurística determinística sobre Score; scripts/reduce_midi.py exporta MIDI e relatório rastreável. Três trilhas, um canal de piano; restrições consideram notas sustentadas. Sem dependências novas. Regras e limitações em docs/REDUCER.md.

## Bloco 3.2 — renderização offline
packages/music/render.py chama a biblioteca nativa FluidSynth via ctypes, agenda notas no tempo absoluto e grava PCM em blocos. FFmpeg codifica MP3. Sem dispositivo de áudio, GPU ou dependência Python adicional. Entrada reduzida limitada, destino novo e relatório de reprodução. Documentação: docs/RENDERER.md.

## Bloco 3.3 — integração web experimental
POST /api/experimental/piano recebe MIDI binário até 5 MiB/120 s; reduz e renderiza em worker thread com exclusão por processo. AnyIO não abandona trabalho ao cancelar, preservando limpeza/lock. Temporários removidos ao terminar; resposta JSON contém arquivos base64 e relatórios. React cria blobs para player/downloads e libera URLs ao trocar entrada/desmontar. Sem histórico, filas ou persistência de resultados.

## Planejado — referências por URL
Adicionar uma referência de origem separada do arquivo de áudio armazenado, com metadados e estado de acesso independentes. Arquivo local e URL podem coexistir no mesmo exemplo sem perda de identidade. Reutilizar a abstração no Laboratório e no Estúdio; migração/backup futuros preservam registros atuais. Player incorporado não disponibiliza áudio ao analisador. Obtenção futura condicionada a meio autorizado e validações de rede/mídia. Especificação: docs/URL_IMPORT.md. Nenhuma alteração de código neste checkpoint.

## MP3-2a — preparação reutilizável
packages/music/audio_clip.py valida arquivo local com FFprobe e decodifica trecho limitado por FFmpeg; saída mono PCM16/22.050 Hz. Cache identificado por hash de entrada/configuração/versão FFmpeg, com integridade da saída conferida antes da reutilização. scripts/prepare_audio_clip.py é operado pelo agente. Não há mudanças na API, frontend, armazenamento web ou adaptador de transcrição.

## Bloco 4.1 — população simbólica
packages/music/population.py cria configurações únicas do redutor, com baseline, seed local e manifesto verificável. generate_proposals reutiliza uma representação Score, exporta MIDI e conta equivalência de notas geradas. CLI registra geração 0; nenhum avaliador ou rede independente treinada. docs/POPULATION.md define o espaço inicial e limites.

## Bloco 4.2 — avaliação da população
packages/music/ranking.py usa generate_proposals e evaluate sobre uma referência alinhada. Cache por hash do MIDI em cada chamada; relatórios detalhados compartilhados por chave. Ranking e contribuições explícitas, falhas nulas, empates sem desempate musical. scripts/rank_population.py salva manifesto e relatório com hashes. Pesos iniciais não constituem currículo ou modelo treinado.

## Diagnóstico 4.2a — áudio-objetivo
Experimentos isolados align_reference.py/compare_audio_pair.py; time_map.py converte notas da referência por mapa temporal monotônico. Fonte transcrita reutilizada e mapeamento independente dos candidatos. Hashes vinculam gravações. Relatório marca diagnóstico e impede autorização de treinamento (flag a ser respeitada pelo futuro consumidor). Sem integração ao frontend ou alteração da população/evaluador base.

## Bloco 4.3 — reprodução
packages/music/evolution.py transforma um manifesto e seu ranking supervisionado em nova geração imutável. Valida hash/geração e bloqueia diagnósticos; elites, recombinação uniforme, mutação e imigrantes dentro do espaço finito existente. CLI de um ciclo em scripts/evolve_once.py. Detalhes em docs/EVOLUTION.md.

## Bloco 4.4 — sessões
packages/music/session.py coordena avaliação/reprodução por geração e persiste envelopes JSON atômicos, com hashes encadeados e configuração vinculada aos arquivos de entrada e código. Usa fcntl no servidor Linux e sementes derivadas por geração. CLI scripts/evolve_session.py inicia/retoma com limite por execução; sem fila web neste bloco. Dados privados em data/ exigem backup separado do Git.

## Bloco 4.5 — portabilidade
services/session_backup.py exporta snapshots privados sob lock e restaura ZIP por lista de nomes permitidos, limites e validação integral antes de publicar destino novo. Mantido separado do código musical para preservar hashes das sessões 4.4. Scripts/session_backup.py fornece CLI; não executa conteúdo importado.

## Bloco 4.6 — histórico web
services/api/sessions.py expõe leitura limitada e validada dos checkpoints sem iniciar evolução; EvolutionHistory.tsx mostra sessões e tabela de gerações. Processamento síncrono de leitura no pool do FastAPI. Nenhum código musical alterado, preservando hashes das sessões.
