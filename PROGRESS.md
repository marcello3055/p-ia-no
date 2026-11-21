# Progresso — Bloco 4.15 concluído
21/11/2026. Anterior remoto 7801207c4992716d1547c65b61f0986e4ce28bcf. O commit deste documento identifica o checkpoint atual.

Criado experimento de limpeza (F0,5) e proteção de correspondências. Reutilizados 91 candidatos MIDI distintos dos relatórios 4.14, mais avaliação do preferido 4.13 sob as mesmas tolerâncias. Sem transcrição, geração, renderização ou instalação nova. Motor, API e sessões intactos.

Preferido humano de 56 notas supera baseline no novo componente (0,18152 vs 0,15815), mas perde 2 das 13 correspondências de referência e é bloqueado pela proteção estrita. Essa regra NÃO reconhece melodia; não interpretar a perda como perda melódica. Melhor elegível tem 81 notas; sem escuta e sem alegação de melhora musical. Experimento não integrado ao treinamento.

Três testes controlados passaram (extras, perda de correspondência/silêncio, oitava, beta inválido); análise real executada. Resultados docs/CLEANLINESS_REVIEW_RESULT.json, método docs/CLEANLINESS_REVIEW.md. Sem novo áudio para usuário ouvir. Feedback permanece inalterado: prefere ligeiramente o candidato de 56 notas por limpeza.

## Próximo bloco 4.16 — aguardar autorização
Guia melódico heurístico e testes que distingam retirada de acompanhamento e de melodia; avaliar proteção nos candidatos existentes. Não reabrir auditorias de alinhamento, não aumentar gerações sem objetivo. Interface de treinamento por MP3 e biblioteca de arranjadores aprovados continuam pendentes.

## Recuperação
4.14 ZIP libfile_111a013223488191b07808261aa9bb68; 4.13 ZIP libfile_907b506dc950819197873da47d5fa161. Recuperação de sessões exige checkout correspondente ao hash de código. Nenhum arquivo desses pilotos foi alterado neste bloco.
