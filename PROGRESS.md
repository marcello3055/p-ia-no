# Progresso — Bloco 4.11, auditoria do alinhamento interno
Data: 17/11/2026. Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior remoto: d92493b86c36b53e8bf583cd7efc1f6181ea4ab3.
O commit deste documento identifica o checkpoint 4.11.

## Encontrado e implementado
Auditoria comprova 18 trechos estacionários no mapa anterior, maior com 2,6989 s de OST, e salto de 1,7254 s na referência. Criada alternativa experimental DTW de passos estritamente crescentes e limitados. Resultado: zero trechos estacionários, maior avanço 0,1865 s. Divergência máxima entre mapas 4,0104 s; isso exige revisão musical, não permite alegar alinhamento validado. Mantidos extremos indicados OST 24,5–50 / piano 20–38.

## Testado
Verificação controlada experiments/check_bounded_alignment.py passou (identidade, extremos, inclinação, auditoria de colapsos, mapas inválidos). Aplicação real aos recortes já existentes, hashes conferidos. Sem nova transcrição, treinamento, alteração de ranking ou renderização. Motor/API/frontend inalterados; sem instalação, GPU ou gasto. Checkpoint/whitespace conferidos.

## Artefatos e limites
docs/ALIGNMENT_AUDIT.md e ALIGNMENT_AUDIT_RESULT.json registram resultados. Mapas completos e features privados em data/alignment-audit-4-11; originais anteriores preservados. Ambos os alinhamentos continuam sem validação musical. training_allowed=false; não alimentar seleção evolutiva com este diagnóstico. As regiões gerais já foram fornecidas pelo usuário e não devem ser pedidas novamente.

## Próximo bloco — 4.12 (aguardar autorização)
Verificar motivos/ataques nos pontos divergentes, principalmente OST 39,5–45,5 s, comparando alternativas de correspondência no piano com os arquivos existentes. Preparar escuta curta se necessária. Depois de validar a comparação, executar primeira sessão experimental do par real. Chrome já reproduziu candidato sintético; Android e avaliação auditiva humana continuam pendentes.
