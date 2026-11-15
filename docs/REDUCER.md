# Redutor experimental — 0.1.0
Bloco 3.1. Algoritmo determinístico, sem aprendizado. Entrada interna Score/MIDI validado; saída MIDI tipo 1, trilha de tempo e duas trilhas de mãos, canal 0 e programa General MIDI 0 (piano acústico). MIDI não contém áudio nem biblioteca de amostras.

## Regras reproduzíveis
Teclas 21–108, duração positiva, sem canal de percussão 9. Divisão fixa: abaixo de 60 mão esquerda; demais mão direita. Por ataque, prioriza graves na esquerda e agudos na direita; empate por intensidade decrescente e índice original. Padrão de três notas simultâneas por mão e alcance máximo de 12 semitons. Configuráveis: divisão 22–108, quantidade 1–5, alcance 0–12.
Notas sustentadas ocupam capacidade/alcance até seu fim. Novas notas incompatíveis são descartadas, não encurtadas. Duplicatas sobrepostas da mesma altura são descartadas; reataques exatamente no fim são permitidos. Não funde duplicatas: a primeira selecionada prevalece, mesmo se outra durar mais. Não transpõe nem inventa acompanhamento. Conserva altura, início, fim e velocidades das selecionadas.

Mapa de tempo normalizado, compassos e armaduras preservados. Instrumentos, pedal, controladores, pitch bend e outros eventos omitidos. Todas as decisões incluem índice da nota de origem e motivo; relatório inclui parâmetros, versão e avisos originais. CLI acrescenta SHA-256 de entrada/saída.

## Execução pelo agente
```sh
.venv/bin/python scripts/reduce_midi.py entrada.mid --output piano.mid --report relatorio.json
```
Destinos novos e distintos; arquivos existentes não são sobrescritos. Falha normal ao salvar remove arquivos criados nessa chamada. Não há garantia transacional contra interrupção abrupta. Entrada limitada a 5 MiB pela leitura existente. Dados musicais continuam fora do Git.

## Limites
Voz mais aguda pode não ser melodia; grave pode não ser baixo principal. Notas sustentadas podem bloquear ataques importantes. Sem análise de função harmônica, saltos, dedilhado, velocidade de execução, arpejos, frases, rubato ou pedal. Respeitar limites simultâneos não comprova execução humana nem qualidade artística. Sem avaliação auditiva/repertório real, API ou interface do redutor neste bloco.
Upload e reprodução de MP3 já existentes são independentes. Transcrição automática do áudio e geração de áudio de piano permanecem etapas futuras. O usuário não precisará converter MP3 para MIDI manualmente no produto final.
