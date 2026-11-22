# Bloco 4.16 — guia melódico inicial
21/11/2026 (data local da sessão).

Implementação experimental em experiments/melody_guide.py. Seleciona notas da referência com duração >=120 ms que sejam a altura mais alta entre as notas elegíveis por pelo menos metade da duração. Esses limites foram definidos antes da análise real, sem ajuste para favorecer o candidato preferido. Notas curtas não mascaram notas sustentadas; percussão excluída. Não equivale a reconhecer a melodia principal: pode confundir acompanhamento agudo, perder melodias internas/graves ou notas rápidas. O código vive fora do motor para preservar hashes das sessões.

Proteção: interseção do guia com correspondências já obtidas pelo baseline. Ausência total de correspondências não libera candidatos por condição vazia. F0,5 do bloco 4.15 continua separado da proteção. Nos testes, remover acompanhamento é permitido, remover nota da voz superior é bloqueado. Isso só demonstra comportamento nas condições controladas.

Testes: seis passaram, cobrindo retirada de acompanhamento versus melodia superior, arpejos graves, pico agudo curto, entrada vazia, guia sem cobertura, silêncio, oitava, limites inválidos e falha conhecida com melodia interna. A fixture da falha confirma a limitação, não acurácia geral. Sem nova inferência, renderização ou treinamento; 91 propostas em cache examinadas.

Tifa: 24 notas no guia. Baseline cobre 5/24, candidato preferido 4/24; proteção bloqueia o preferido pela referência índice 27. Não converter essas frações em percentual da melodia reconhecida: transcrição, alinhamento e heurística são incertos. Entre 91 propostas, seis elegíveis; melhor pela regra tem 81 notas, sem evidência auditiva de melhora. Dados agregados MELODY_GUIDE_RESULT.json. Não promover regra a requisito musical confiável. Feedback humano continua preferindo levemente o de 56 notas.

Próximo 4.17: integrar os componentes experimentais de limpeza e cobertura do guia como indicadores explicáveis e opcionais na avaliação, mantendo pontuações separadas e o avaliador anterior disponível. Guia incerto não deverá bloquear sozinho um candidato. Realizar piloto curto com configuração persistida e comparar resultado audível se houver alteração; não insistir em calibrar heurística indefinidamente neste único trecho. Sem modificar arranjador aprovado ou histórico.
