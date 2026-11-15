# Avaliador simbólico inicial — Bloco 2.2

## Uso pelo agente
`packages.music.evaluate.evaluate(reference, candidate, config)` recebe dois Scores do leitor MIDI. CLI: `.venv/bin/python scripts/compare_midi.py referencia.mid candidato.mid --output relatorio.json`. Não sobrescreve relatórios. Há painel de comparação na aba Treinamento desde o Bloco 2.3.

## Critérios e interpretação
- pitch_inventory_only: interseção de multiconjuntos de alturas, ignorando tempo. Diagnóstico; não é medida de harmonia ou melodia.
- pitch_and_onset: altura MIDI exata e início dentro da tolerância, em correspondência um a um.
- pitch_onset_and_duration: subconjunto dos mesmos pares que satisfaz tolerância de duração.
Em cada critério: precisão = correspondências / notas candidatas; recall = correspondências / notas de referência; F1 é média harmônica. Valores de 0 a 1. Candidato vazio: zero por convenção. Referência vazia após filtros: erro, não pontuação perfeita.
Lista de correspondências e índices sem par permite inspecionar diferenças. Os índices referem-se a Score.notes, antes da exclusão de percussão. Erros médios absolutos de início/duração usam somente pares altura+início; retorno null quando não há pares, nunca falso erro zero. Comparar esses erros sempre junto com cobertura e contagens.

## Pareamento
Agrupar por altura, ordenar por início e índice original e percorrer as duas listas cronologicamente. Cada nota participa uma vez; não há reutilização para melhorar a pontuação. Com tolerância uniforme de início, maximiza a quantidade de correspondências possíveis para a altura; não minimiza erro temporal nem maximiza acertos de duração. Empates são determinísticos pela ordem dos índices. Duplicações em outras trilhas não são colapsadas.

## Configuração
Padrão: time_unit=quarters, onset_tolerance=0.1, duration_absolute_tolerance=0.1, duration_relative_tolerance=0.2, include_percussion=false. Quarters significa semínimas, não necessariamente pulsação do compasso. Em seconds, os dois primeiros limites passam a ser segundos. A duração aceita erro <= max(limite absoluto, fração × duração da referência). Tolerâncias finitas e não negativas. Folga numérica de 1e-12 nas comparações de limite.
Índice de canal 9 (canal 10 MIDI) é excluído por padrão devido à convenção de percussão; opção para incluir. Não exigir mesmo canal ou trilha, pois a distribuição pode mudar entre arranjos.

## Limites
Sem alinhamento automático, remoção de introdução, normalização de tonalidade, DTW ou compensação de rubato. Quarters ignora diferenças do mapa de andamento; seconds usa o mapa individual de cada MIDI. Não chamar ausência de correspondência de erro artístico: arranjo válido pode diferir da referência.
Sem avaliação de motivos, harmonia funcional, contraponto, mãos, tocabilidade, pedal, timbre ou expressividade. Pitch é a tecla MIDI (pitch bend não altera a altura comparada). Duração é pressionamento da tecla. Sem nota geral ponderada ou conclusão de aprendizado/generalização. Avisos do leitor são propagados.

## Validação
11 testes novos: identidade, ausência/excesso/altura incorreta, duplicata sem dupla contagem, caso em que vizinho mais próximo perderia correspondência, fronteira da tolerância, duração, andamento/resolução, entradas vazias, tolerâncias inválidas, filtro de percussão e relatório CLI sem sobrescrita. Apenas exemplos sintéticos; validação perceptual e repertório real pendentes. Nenhuma dependência nova.

## API e interface — Bloco 2.3
POST /api/midi/compare: application/octet-stream com bytes referência+candidato; query reference_bytes delimita os dois arquivos. Até 5 MiB cada, 10 MiB total, limite contado durante streaming. Configuração em query: time_unit (quarters/seconds), onset_tolerance e duration_tolerance entre 0 e 10, duration_relative entre 0 e 1. Percussão excluída. Um pedido por processo; ocupado retorna 503. Análise em thread para não bloquear o event loop. Sem gravação de MIDI ou relatório em disco. Hashes dos dois arquivos no relatório para rastreabilidade.
Interface mostra os três critérios, contagens, erros e limites; permite baixar JSON com o relatório completo e nomes dos arquivos. Não conserva resultado após reload. Envio sem progresso percentual, mas com estado Enviando e comparando. Timeout cliente 60 s não é garantia de interrupção imediata da thread no servidor. Ainda restrito a desenvolvimento, sem autenticação/publicação.

## Diagnósticos de classes de altura e ritmo — Bloco 2.4
Avaliador versão 0.2.0; campos adicionais preservam métricas anteriores. Usam as mesmas notas filtradas, unidade temporal e exclusão de percussão.

Classes de altura = pitch mod 12. Distribuição global: somar duração das notas por classe, normalizar cada vetor e somar mínimos correspondentes (0–1). Ignora oitavas e ordem; dobramentos podem alterar pesos. Se referência não tem duração positiva, retorna null; candidato vazio com referência positiva resulta zero.
Coincidência temporal: varrer inícios/fins e integrar o número de classes ativas compartilhadas, dividido pela integral do número de classes ativas na união (Jaccard temporal). Dobramentos simultâneos na mesma classe contam uma vez; silêncios comuns não aumentam a pontuação. Se a união tem duração zero, retorna null. Não identifica acordes, tonalidade, função harmônica ou progressão; depende do alinhamento existente.

Ritmo: inícios exatamente simultâneos formam um ataque, independentemente de densidade do acorde ou alturas. Pareamento cronológico um a um usa tolerância de início configurada; relata precisão/recall/F1 e contagens. Não agrupa arpejos nem ataques quase simultâneos em um único ataque.
Padrão relativo: intervalos consecutivos entre ataques, divididos pela soma de cada sequência. Similaridade = 1 − metade da distância L1 entre os vetores normalizados. Calculado somente se há pelo menos três ataques por arquivo e contagens iguais; caso contrário retorna null e explicação. Ignora deslocamento inicial e escala uniforme de tempo, não rubato; não corrige correspondência equivocada por introdução/repetição. Contagem igual não garante seções correspondentes.

Nove testes novos cobrem oitavas, ordem, acordes parciais, silêncio comum, dobramentos, escala/deslocamento, mudança de padrão, poucos ataques, contagem desigual, duração zero e escolha da unidade temporal. Nenhum deles comprova qualidade auditiva ou generalização.
