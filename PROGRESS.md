# Progresso — Bloco 4.2
Data: 16/11/2026. Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: 8f384acf0c45f7d4b1959ea99c449d3e8fc6343c.
O commit deste documento é o checkpoint 4.2.

## Implementado
Avaliador simbólico ligado à população, com quatro critérios (altura/início, duração, classes de altura temporais e ataques), pesos configuráveis/normalizados e contribuições explícitas. Ranking reproduzível com empates de mesma posição, todos os melhores listados, falhas sem nota. Cache de MIDIs idênticos evita avaliação redundante na chamada. CLI salva manifesto, ranking, detalhes e hashes da fonte/referência em pasta nova. Sem transcrição/renderização, dependência nova, GPU ou gasto.

## Testado
81 testes passaram (76 anteriores + 5 novos): vencedor conhecido, soma de contribuições, pesos inválidos, empates/cache, determinismo, referência inválida, candidatos falhos, replay CLI e recusa de sobrescrita. CLI em exemplo sintético: 100 candidatos avaliados, zero falhas, 4 avaliações únicas, score máximo 1,000, baseline 0,525. Referência simples deliberada (8 notas de extremos em fonte de 40); diferença 0,475 não é evolução nem melhoria auditiva. Checkpoint/whitespace verificados; frontend inalterado, build/Chrome não repetidos.

## Limites
Score mede correspondência a uma referência alinhada; não qualidade artística, melodia principal, harmonia funcional ou expressão. Pesos ainda convencionais; critérios se sobrepõem. Sem currículo, restrições mínimas por critério, seleção, mutação, recombinação ou aprendizado. Cache apenas por chamada; relatórios de execução locais fora do Git e sem histórico/backup web. Configurações e testes reproduzíveis versionados. Referência MIDI vazia é rejeitada.
Prova Tifa aceita pelo usuário como suficiente para avançar (melodia subjetiva 7/10, notas extras); não reprocessada, não usada como referência simbólica nem refinada neste bloco. Planejamento URL preservado.

## Próximo bloco recomendado — 4.3 (aguardar autorização)
Implementar e testar um ciclo controlado de seleção/reprodução com mutação, recombinação e manutenção de diversidade. Em blocos posteriores: várias gerações, currículo com proteção dos critérios, checkpoints/histórico, painel e escuta dos melhores. Sem promessa de melhoria auditiva a partir do ranking numérico.
