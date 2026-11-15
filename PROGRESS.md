# Progresso — Bloco 2.4
Data: 14/11/2026 (fuso do usuário). Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: ba08d889bb7c11196fa695283d999b94917f4104.
O commit deste documento é o checkpoint 2.4.

## Implementado
- Classes de altura: distribuição global ponderada por duração e coincidência temporal (Jaccard de classes ativas).
- Ritmo: ataques únicos, correspondência temporal e similaridade de intervalos relativos normalizados.
- null e explicação para casos sem duração suficiente, poucos ataques ou quantidades incompatíveis.
- Campos no relatório JSON/API e textos explicativos no painel. evaluator_version 0.2.0. Métricas antigas preservadas.

## Validação
- 53 testes aprovados: 44 anteriores + 9 novos.
- Casos controlados: oitavas, mesma distribuição com ordem alterada, acordes parciais, silêncio, dobramentos, escala/deslocamento temporal, padrões diferentes, quantidades insuficientes/desiguais, zero duração e segundos versus semínimas.
- TypeScript/build Vite aprovados. Testes da API exercitam o retorno ampliado.
- Não houve nova inspeção visual no navegador neste bloco; Android e repertório real permanecem pendentes. Sem avaliação auditiva ou dados do usuário.

## Limites
Sem reconhecimento de acordes/tonalidade/função harmônica. Sem alinhamento de seções, rubato, notas expressivas, tocabilidade ou qualidade artística. Padrão relativo só comparável com mesmos números de ataques e pelo menos três; não prova correspondência de seções. Métricas não comprovam aprendizado/generalização.
Sem transcrição MP3, treinamento ou arranjo gerado. Sem dependência nova/GPU/custo externo. Hospedagem permanente, autenticação e backup automático seguem pendentes. GitHub é fonte principal; dados privados fora do Git e sem force-push.

## Próximo bloco — 3.1 (aguardar autorização)
Primeiro redutor simbólico experimental: seleção de vozes e distribuição básica entre mãos a partir de MIDI, geração de MIDI de piano e testes de limites de execução. Heurísticas documentadas, sem alegar modelo treinado. Renderização de áudio ficará para outro bloco.

## Retomada em 15/11/2026
A gravação remota anterior foi impedida pelo limite de uso antes de criar a árvore no GitHub. Arquivos locais e commit 4393cca preservados e conferidos; main remoto ainda estava em ba08d889bb7c11196fa695283d999b94917f4104. Retomada dedicada a concluir a sincronização 2.4, sem repetir instalações/testes já aprovados ou iniciar o Bloco 3.1.
