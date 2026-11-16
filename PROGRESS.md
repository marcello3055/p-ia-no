# Progresso — 4.2b, correção de regiões correspondentes
Data: 16/11/2026. Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: 08de52b49c0763a7cb5b860e7e305ae8b622a8ee.
O commit deste documento é o checkpoint 4.2b.

## Correção e execução
Usuário rejeitou alinhamento global anterior. Região indicada: OST começa entre 24 e 25 s e termina em 50; piano 20 s até fim do segundo 37. Adotados OST 24,5–50 s (25,5 s) e piano 20–38 s (18 s), preservando incerteza do início OST. Novo DTW ponta a ponta dentro dessas regiões, corredor normalizado 15%, extremos fixos; sem busca de outros trechos.
Nova transcrição do trecho ampliado: 126 notas OST, 83 no baseline; 79 notas de referência, todas mapeadas. Ranking recalculado: 100 candidatos, 62 avaliações únicas, baseline e máximo 0,212052. Score diagnóstico, não precisão/qualidade ou evidência de melhora. Regiões reconhecidas como indicadas pelo usuário; mapa interno ainda não validado. training_allowed=false, nenhuma seleção/reprodução.

## Verificado
84 testes passaram. Verificação sintética adicional de DTW ancorado: identidade, extremos exatos, monotonicidade, corredor e transformação temporal da nota. Script de verificação preservado. Inferências/ranking reais concluídos; hashes vinculam fonte/referência. Checkpoint e whitespace conferidos. Sem dependência nova, GPU ou gasto; frontend inalterado. Não houve nova escuta humana da saída.

## Preservação e limites
Áudios/estimativas/relatórios privados fora do Git em data/source-corrected-01 e data/pair-corrected-01, pacote corrigido preparado. Relatório anterior em data/pair-01 marcado como rejeitado pelo usuário; histórico preservado, não reutilizar pontuações. Arquivos originais intactos. DTW interno toca quase a borda do corredor (desvio 0,14971), requer cautela; 24,5 s é escolha aproximada. Transcrições têm incerteza e velocidades não recuperam interpretação. Melhor score igual ao baseline não implica incapacidade dos futuros bots, apenas resultado deste espaço inicial/critério. Docs/PAIRED_AUDIO.md detalha métodos.

## Próximo bloco recomendado — 4.3 (aguardar autorização)
Implementar seleção/reprodução, mutação/recombinação e diversidade com exemplos simbólicos controlados e testes. Manter o par real corrigido como diagnóstico, recusando uso automático de ranking com training_allowed=false. Não pedir novamente identificação da mesma região, já fornecida pelo usuário. Currículo e validação de alinhamento interno seguem pendentes, sem bloquear implementação/testes do motor.
