# Auditoria temporal — Bloco 4.11
Data: 17/11/2026.

## Problema comprovado
O mapa interno anterior continha 18 trechos de tempo estacionário. O maior fazia 2,6989 segundos da fonte corresponderem ao mesmo instante da referência. O maior avanço entre dois pontos adjacentes da referência era 1,7254 s; inclinação local máxima 18,5395. Isso pode distorcer duração/início das notas quando o mapa é invertido pelo avaliador. Não demonstra que toda a correspondência estava errada, mas impede aprová-la apenas com base nos extremos indicados pelo usuário.

## Alternativa experimental implementada
DTW com passos (1,1), (1,2), (2,1), avanço obrigatório em ambos os eixos, interpolação nos frames omitidos. Mesmo chroma, corredor normalizado 15%, mesmas regiões OST 24,5–50 e piano 20–38, extremos fixos. Alternativa salva separadamente; nenhum ranking ou alinhamento anterior sobrescrito. Fonte e alvo verificados por hash dos recortes. Aproveitadas gravações/transcrições existentes; não houve nova inferência. Features de áudio calculadas e salvas para reaproveitamento.

Na alternativa, não há trechos estacionários; maior avanço na referência 0,1865 s e inclinações locais entre 0,5011 e 2,0043. Valores dependem da discretização dos frames. A divergência máxima em relação ao mapa anterior é 4,0104 s. Restrições temporais corrigem deformação extrema, mas NÃO provam que motivos/ataques musicais correspondem. Custos de caminhos com passos distintos não devem ser usados como comparação direta de qualidade. Status experimental; training_allowed=false.

## Testado
experiments/check_bounded_alignment.py passou no ambiente de áudio existente: mapa identidade, extremos fixos com durações diferentes, inclinação estritamente positiva/limitada, detecção de trecho estacionário e rejeição de mapas inválidos. Execução real em dois recortes produziu relatório agregado docs/ALIGNMENT_AUDIT_RESULT.json. Nenhum teste anterior foi apresentado como nova execução; motor, API e frontend inalterados. Sem instalação, GPU ou gasto.

```sh
.venv-audio/bin/python experiments/check_bounded_alignment.py
.venv-audio/bin/python experiments/audit_alignment.py --pair data/pair-corrected-01 --output data/alignment-audit-4-11
```
Saída exige pasta nova. Dados completos e features privados em data/alignment-audit-4-11, fora do Git. Código e métricas agregadas preservados no GitHub; podem regenerar a alternativa com recortes originais. Não alterar a versão aprovada do arranjador (ainda inexistente).

## Próximo bloco
Examinar correspondências de motivos/ataques nos pontos mais divergentes, especialmente OST aproximadamente 39,5–45,5 s: mapa anterior aponta piano 29,51–32,22, alternativa 32,65–35,70. Preparar comparação curta com os arquivos existentes, sem pedir novamente ao usuário quais são as regiões gerais. Se a correspondência continuar ambígua, sinalizar exatamente qual marco interno precisa de confirmação. Não iniciar seleção com ranking diagnóstico.
