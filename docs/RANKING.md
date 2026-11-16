# Classificação supervisionada inicial — Bloco 4.2
Liga a população ao avaliador simbólico existente, usando uma referência de piano MIDI já alinhada. Não transcreve MP3, não treina redes e não realiza seleção/reprodução. A versão de Tifa não possui referência simbólica conferida e não recebeu pontuação automática neste bloco.

## Critérios e pesos
Soma ponderada em escala 0–1:
- 0,50: F1 de altura exata e início.
- 0,25: F1 de altura, início e duração.
- 0,15: Jaccard temporal de classes de altura ativas.
- 0,10: F1 de ataques únicos.
Pesos são escolhas iniciais convencionais, não aprendidas/calibradas. Critérios se sobrepõem: duração depende também de altura/início, e classes/ataques reaproveitam informações das notas; não interpretar como dimensões independentes. Classes de altura não reconhecem função harmônica; ataques não avaliam fraseado. Não há reconhecimento explícito de melodia principal ou avaliação de expressão/tocabilidade.

Pesos configuráveis com as quatro chaves pitch_onset, duration, pitch_classes e attacks; números finitos, não negativos, soma positiva; normalização pela soma. Critério indefinido com peso positivo impede ranking, em vez de inventar nota. Zero desativa contribuição mas mantém diagnóstico. Não é ainda o currículo por fases ou otimização multiobjetivo: mínimos e proteção de critérios serão implementados em blocos futuros.

Tolerâncias padrão: unidade semínimas; início 0,1; duração máximo(0,1; 20% da referência); percussão excluída. API Python aceita EvaluationConfig completo; CLI permite escolher unidade quarters/seconds. Referência vazia/inválida é rejeitada antes da geração. Sem alinhamento automático de seções/rubato.

## Ranking e cache
Scores individuais, contribuições ponderadas e avaliação detalhada são registrados. Ranking decrescente, empates com mesmo score recebem a mesma posição (1,1,3); ID ordena apenas apresentação reproduzível. Todos os empatados no topo são listados. Sem desempate musical inventado. Falhas ficam com score/rank nulos e fora da classificação; nenhuma saída válida resulta best_score=null.
Cache por bytes MIDI gerados dentro desta chamada evita repetir métricas de candidatos idênticos; guarda avaliação detalhada uma vez e referência por chave em cada candidato. Não persiste cache entre sessões. Reporta diferença para baseline, sem chamá-la de aprendizado ou melhoria auditiva.

## Execução pelo agente
```sh
.venv/bin/python scripts/rank_population.py fonte.mid referencia.mid --output-dir data/ranking-novo --size 100 --seed 0
```
Pode usar --population com manifesto anterior e --weights com JSON dos quatro pesos. A pasta deve ser nova; contém population.json e ranking.json, hashes da fonte/referência, versões, configuração, critérios e resultados. Nenhum áudio é renderizado. Checkpoint local de experimento, ainda sem histórico web/backup automático; guardar os artefatos privados separadamente do Git.

## Evidência
81 testes passaram (76 anteriores + 5 novos), cobrindo ranking correto em caso conhecido, contribuições, cache, empates, reprodução exata, pesos, referência inválida, falhas e CLI sem sobrescrita.
CLI executado em fonte sintética de 40 notas e referência controlada de 8 notas (somente extremos): 100 candidatos avaliados, zero falhas, 4 avaliações distintas; melhor score 1,000, baseline 0,525, diferença 0,475. Referência deliberadamente simples para verificar seleção por correspondência; não demonstra qualidade em música real, evolução ou generalização. Registro local data/ranking-4-2.

Próximo bloco 4.3: seleção/reprodução, mutação/recombinação e preservação de diversidade em um ciclo controlado; checkpoints de muitas gerações e painel serão incrementos posteriores.
