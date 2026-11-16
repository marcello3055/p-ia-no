# Progresso — diagnóstico de par real 4.2a
Data: 16/11/2026. Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: a30d2dc3714cf9e2d606dca70c291e7885709689.
O commit deste documento é o checkpoint 4.2a.

## Escopo e execução
Usuário esclareceu que o objetivo é comparar contra o piano enviado; rankings anteriores eram sintéticos. Agora: OST 30–50 s transcrita anteriormente reutilizada; piano fornecido analisado por cromas/DTW e transcrito em trecho proposto. Scripts novos experimentais e módulo de mapeamento temporal. Sem nova dependência, GPU, gasto ou extração de URLs.
Alinhamento propõe piano 4,830–18,204 s, com alternativas próximas: não validado. 42 notas estimadas na janela com margem, 37 mapeadas, 5 externas excluídas, 3 truncadas nas bordas. 100 candidatos comparados, 63 avaliações únicas. Baseline 0,173571 e máximo 0,183768 são diagnósticos, não precisão ou melhoria artística. status diagnostic_only_alignment_unverified, training_allowed=false. Sem seleção/reprodução.

## Testado
84 testes passaram (81 anteriores + 3 para mapa temporal). Verificação adicional DTW com o mesmo trecho deu identidade/custo zero; não valida correspondência entre gravações. Inferência/ranking reais concluídos, hashes de fonte/referência conferidos. Checkpoint/whitespace verificados. Nenhum teste de escuta humana concluído nem mudança de frontend. Referências web DTW tentadas retornaram 404; teste usa librosa instalada.

## Persistência e limitações
Mídia/notas/relatórios detalhados privados em data/pair-01, fora do Git; pacote privado preparado para recuperação e comparação dos recortes. Docs/PAIRED_AUDIO.md contém métodos e números agregados, sem música. Fonte/candidato têm erros de transcrição; cromas ignoram oitavas; repetições e patamares podem distorcer correspondência. Tolerância 200 ms não calibrada. Ainda falta mecanismo de correção manual na UI; scripts internos não são endpoints públicos. Flag de bloqueio deverá ser respeitada pelo futuro motor de seleção.

## Próximo bloco recomendado (aguardar validação dos recortes)
Confirmar ou corrigir trecho do piano correspondente à OST 30–50 s. Se incorreto, definir âncoras/trecho manual e recalcular mapa/referência com cache, antes de 4.3. Não treinar bots contra trecho errado nem atribuir pontuação baixa somente ao arranjo. Manter decisão de não refinar notas extras agora e preservar planejamento de URLs.
