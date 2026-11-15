# Avaliador simbólico inicial — Bloco 2.2

## Uso pelo agente
`packages.music.evaluate.evaluate(reference, candidate, config)` recebe dois Scores do leitor MIDI. CLI: `.venv/bin/python scripts/compare_midi.py referencia.mid candidato.mid --output relatorio.json`. Não sobrescreve relatórios. Ainda não há upload de MIDI ou painel de comparação no site.

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
