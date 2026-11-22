# Progresso — Bloco 4.16 concluído
21/11/2026. Anterior remoto 434c4452aa0f2bdffab73a25002ba671778563f5. O commit deste documento identifica o checkpoint atual.

Guia melódico heurístico implementado fora do motor (experiments/melody_guide.py), com proteção baseada nas correspondências do baseline e resultados por critério. Seis testes controlados passaram. Inspecionadas 91 propostas em cache; sem treinamento, áudio novo, transcrição ou gasto. Nenhum hash/código de sessão modificado.

Tifa: guia 24 notas, baseline corresponde 5, preferido humano 4. Não é percentual de reconhecimento da melodia. Regra estrita continua bloqueando preferido por uma nota e NÃO foi adotada como bloqueio de produção. Melhor elegível 81 notas, sem melhora auditiva demonstrada. Feedback humano preservado. docs/MELODY_GUIDE.md documenta método e falhas, docs/MELODY_GUIDE_RESULT.json contém resultados.

## Próximo 4.17 — aguardar autorização
Integrar limpeza e cobertura do guia como indicadores experimentais opcionais, explicáveis e persistentes; não usar heurística incerta como bloqueio absoluto. Piloto curto e comparação audível se resultado mudar. Evitar novas rodadas de auditoria/calibração sem entrega. Interface MP3 e biblioteca de arranjadores aprovados continuam pendentes.

## Recuperação
4.14 ZIP libfile_111a013223488191b07808261aa9bb68; 4.13 ZIP libfile_907b506dc950819197873da47d5fa161. Retomada de cada sessão exige código original; nenhum arquivo dos pilotos alterado neste bloco.
