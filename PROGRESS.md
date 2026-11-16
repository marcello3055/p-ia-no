# Progresso — MP3-2b
Data: 16/11/2026. Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: 7c6b557b70dd7acf5fca771c9d0ecb10c0eadcbf.
O commit deste documento é o checkpoint MP3-2b.

## Implementado e executado
Novo script experiments/transcribe_clip.py integra preparação de arquivo local, transcrição Basic Pitch/ONNX CPU e redutor/renderizador existentes. Executado no arquivo de Tifa’s Theme enviado pelo usuário, trecho 30–50 s. Resultado: 99 notas estimadas; 65 preservadas e 34 descartadas (24 polifonia, 10 alcance). Piano WAV/MP3 com 23 s incluindo cauda. Nenhum treinamento, GPU, serviço pago ou extração de URL.
Mídia e relatório detalhado privados em data/real-clip-01; não enviar áudios, MIDIs derivados ou ativações ao Git. Pacote privado de entrega contém o recorte, saída de piano, MIDI, transcrição bruta, ativações e relatório para continuidade.

## Verificações
Inferência real completa em ~0,813 s (não extrapolar), pico RSS processo 301,78 MiB. MIDI relido com 65 notas; MP3 decodificado integralmente sem erro; áudio não silencioso/não saturado, pico 1410/32768. Relatório confirma ausência de métricas de referência e recorte de 20 s. Script compila. Checkpoint/whitespace verificados. Código da aplicação não mudou; 71 testes anteriores não repetidos nem contabilizados como nova execução.

## Limites
Sem referência MIDI conferida, sem acurácia calculada e sem avaliação auditiva humana concluída. Distribuição 15 notas esquerda/50 direita não prova função musical. Intensidade baseada em ativação não equivale a dinâmica recuperada. Redução experimental pode perder melodia/baixo ou conservar erros de transcrição. Sem pedal/expressividade nova, integração de transcrição à interface, arranjador aprovado ou análise integral. Docs: docs/REAL_AUDIO_PROBE.md. Planejamento URL preservado.

## Próximo bloco recomendado — MP3-2c (aguardar avaliação e autorização)
Usuário compara o recorte original e o piano gerado, identifica problema prioritário (melodia, notas estranhas, acompanhamento ou timbre). Testar uma intervenção focal e comparar A/B com este baseline, sem treinar sobre erros não inspecionados. Baseline privado deve ser recuperado do pacote entregue se os arquivos temporários expirarem.
