# Verificação de escuta e disponibilidade — 4.10
Data: 17/11/2026.

## Ensaio reproduzível
```sh
.venv/bin/python scripts/create_listening_demo.py --output data/demo-escuta-4-10
```
Cria fonte sintética de oito ataques com acordes, referência de baixo/melodia, 100 candidatos e gerações 0/1, com source.mid e reference.mid necessários à escuta. Pasta precisa ser nova; tentativa de reutilizar destino foi recusada. Sessão é explicitamente identificada como demonstração, nunca como recuperação da sessão antiga ou treino com Tifa. Não requer nenhum arquivo privado.

## Chrome observado
A sessão demo-escuta-4-10 carregou no painel. Geração 1, candidato candidate-03b5891323b6f341: 16 notas. Expandir → Preparar áudio de piano mostrou estado de preparo, depois player e link MP3. Play alterou controle para pause. Leitura do elemento de áudio: duração 6,95 s, currentTime 0,181178 s e paused=false; observação posterior currentTime 6,815959 s, error=null. Confirma processamento e avanço da reprodução no navegador, não avaliação subjetiva do som. Não se afirmou término completo ou download verificado. Android não testado.

Melhor score 1,0 em ambas as gerações é característica do exemplo controlado, não melhoria demonstrada. Os 117 testes do bloco anterior não foram repetidos: nenhum motor/API/player foi alterado neste bloco. Script novo efetivamente executado; documentação e whitespace conferidos.

## Par Tifa disponível
Dois originais MP3 em ../upload/ encontrados por correspondência SHA-256 com metadados salvos. Recortes data/pair-corrected-01/source/clip.wav (OST 24,5–50 s) e reference/clip.wav (piano 20–38 s) conferidos contra respectivos hashes. Não houve necessidade de reenviar ou transcrever novamente.

MIDI de transcrição OST legível com 126 notas; redução inicial com 83; transcrição de referência legível com 79. Estes números são estimativas de transcrição, não acurácia. Ranking salvo permanece diagnostic_only_internal_warp_unverified, training_allowed=false. Alinhamento interno não foi validado por esta verificação de arquivos. Não habilitar reprodução evolutiva do par real apenas porque os arquivos existem.

## Próxima tarefa
Verificar a correspondência temporal interna do par corrigido usando artefatos já calculados, procurando erros de frase/alinhamento que distorçam o avaliador. Preparar comparação auditiva curta se necessário, preservando regiões fornecidas pelo usuário. Nenhuma nova expansão de painel é necessária antes desse marco.
