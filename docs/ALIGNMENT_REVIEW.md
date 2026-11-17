# Bloco 4.12 — conferência limitada e decisão de escopo
17/11/2026

Implementados diagnóstico de notas em cache e montagem de escuta sem alteração de velocidade. Os testes controlados passaram: notas iguais/diferentes, equivalência de oitava explicitamente limitada, silêncio como ausência de evidência, cortes PCM exatos e rejeição de limites inválidos. MP3 real gerado, duração verificada de 14,81 s. Não houve escuta subjetiva nem nova transcrição.

O mapa limitado do 4.11 não demonstrou melhora musical: similaridade média de classes de notas 0,597 contra 0,699 do anterior; coincidências de ataques 40/126 contra 61/126. Métricas diagnósticas, NÃO notas de qualidade musical, precisão ou revocação. O anterior pode ser favorecido por colapsos temporais e coincidências muitos-para-um. Transcrições incertas; a origem da transcrição de referência é assumida pela pasta do experimento, sem manifesto próprio de vinculação ao recorte. Hashes registrados no resultado. Não promover nenhum mapa a validado.

## Encerramento da investigação
O usuário questionou a necessidade de sucessivas verificações antes de treinar. Alinhamento perfeito não deve ser pré-condição para um piloto supervisionado explicitamente experimental. Encerrar essa sequência de auditorias e priorizar o ciclo real dos bots. Não pedir novamente regiões globais já informadas.

## Próximo bloco proposto — 4.13
Executar rodada curta, com 100 candidatos e poucas gerações, usando os dois áudios já transcritos e referência de piano. Escolher e registrar correspondência provisória e limitações no manifesto da sessão; preservar os diagnósticos com training_allowed=false, sem falsificar validação. Caso o executor recuse diagnósticos, criar autorização experimental explícita e isolada para este piloto, mantendo vedada aprovação automática de arranjador. Ouvir/renderizar apenas baseline e melhor candidato para comparação humana. Não interpretar ganho numérico como aprendizado validado ou generalização. Não aperfeiçoar a transcrição antes do piloto.

## Reprodução
.venv-audio/bin/python experiments/check_alignment_review.py
.venv-audio/bin/python experiments/review_alignment.py --pair data/pair-corrected-01 --source-analysis data/source-corrected-01/report.json --proposed data/alignment-audit-4-11/alignment-proposed.json --output data/alignment-review-4-12

A saída requer pasta nova. Áudios e estimativas ficam fora do Git; código e métricas agregadas preservados. MP3 de comparação preparado, não solicitado como tarefa obrigatória ao usuário.
