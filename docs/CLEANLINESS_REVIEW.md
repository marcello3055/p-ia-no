# Bloco 4.15 — limpeza com preservação conservadora
21/11/2026. Experimento isolado, sem alterar avaliador de produção, sessões ou pesos aprovados.

Implementado F-beta com beta 0,5, que dá mais peso à precisão das correspondências de altura/início que à revocação. Não é penalização por simples número de notas: remover nota que corresponde à referência reduz cobertura. Como proteção inicial, exigiu-se manter os 13 índices da referência correspondentes ao baseline. Essa proteção NÃO identifica melodia; trata correspondências de acompanhamento e de melodia igualmente. Não chamar nota sem correspondência de nota musicalmente errada.

Reutilizados os relatórios das quatro populações 4.14 (91 MIDIs distintos). Histórico validado antes da leitura; nenhuma população gerada ou áudio renderizado. O MIDI do candidato preferido 4.13 foi avaliado uma vez sob as mesmas tolerâncias de 200 ms; referência conferida por hash.

Resultado: F0,5 baseline 0,15815; preferido humano 0,18152. Portanto o componente de precisão concorda com essa preferência específica. Entretanto, o preferido preserva 11 das 13 correspondências, faltando índices 2 e 27, e é rejeitado pela proteção estrita. Entre as 6 propostas que passam, a melhor tem 81 notas e preserva as 13 correspondências. Não há evidência de melhoria auditiva desse candidato. Não relaxamos a regra após ver o resultado apenas para fazer a preferência passar.

Testados três casos: notas extras reduzem score, perda de correspondências bloqueia candidato, silêncio não vence; oitava diferente não é tratada como nota preservada; beta inválido é recusado. Três testes passaram. O teste real é evidência de calibração em um único exemplo, não validação geral.

Limitações: correspondências incertas por transcrição/alinhamento; proteção cobre só 13 de 79 notas da referência, não a composição inteira; F0,5 não contempla articulação, harmonia funcional ou expressividade. O experimento é somente offline, training_allowed=false. Resultados explicáveis em CLEANLINESS_REVIEW_RESULT.json; código experiments/cleanliness_review.py. Nenhuma sessão anterior alterada.

Próximo bloco 4.16: implementar guia melódico inicial explicitamente heurístico e testes controlados que diferenciem retirada de acompanhamento de retirada de melodia. Usar os mesmos candidatos para validar a proteção por função, sem nova auditoria de alinhamento ou treinamento longo. Não alegar reconhecimento confiável de melodia até demonstração.
