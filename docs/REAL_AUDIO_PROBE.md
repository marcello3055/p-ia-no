# MP3-2b — primeiro arquivo mult instrumental real
Data: 16/11/2026. Arquivo fornecido pelo usuário nesta conversa: OST de videogame, Tifa’s Theme. O usuário confirmou que o material corresponde ao objetivo. Não foi feita busca, download ou extração do YouTube. Áudio original, recortes, MIDI e notas estimadas não estão no Git.

## Procedimento efetivamente executado
Arquivo de 307,252 s; recorte temporal 30–50 s (20 segundos), escolhido como primeiro ensaio, sem alegar identificação automática de seção. Preparação mono PCM16/22.050 Hz. Basic Pitch 0.4.0, ONNX CPU, thresholds padrão mantidos (.5 onset, .3 frame, 127,7 ms mínimo), sem separação de fontes. Saídas brutas e ativações preservadas privadamente. Novo script experiments/transcribe_clip.py executa preparação → transcrição → representação simbólica → redução → MIDI e WAV/MP3.
O script exige destino novo; não repete automaticamente resultados anteriores. Pode deixar resultados intermediários em caso de falha para diagnóstico; relançar em pasta nova. Inferência está no ambiente isolado .venv-audio; nenhuma alteração da aplicação web.

## Medições — não são acurácia
- 99 notas estimadas, pico de 8 simultâneas; alturas MIDI 53–94.
- Durações estimadas: mínimo 0,139 s, mediana 0,663 s, máximo 3,566 s.
- Redução: 65 notas mantidas, 34 descartadas (24 limite de simultaneidade/mão; 10 alcance/mão).
- Distribuição de saída: 15 notas na esquerda, 50 na direita. Não demonstra preservação correta de baixo/melodia.
- Inferência e pós-processamento: 0,813 s; pico RSS do processo completo 301,78 MiB. Não comparar diretamente a execuções frias nem extrapolar a músicas inteiras.
- Áudio de piano: 23 s (20 s + cauda de 3 s), pico PCM16 1410, não silencioso e sem saturação. Volume modesto; sem normalização nova. MP3 decodificado integralmente sem erro por FFmpeg; MIDI relido e contagem conferida.

## Limitações e decisão
Não existe referência simbólica verificada deste trecho: precisão, recall e F1 permanecem nulos. Não classificamos notas como falsas/verdadeiras apenas pela saída do próprio modelo. Não houve escuta humana aprovada nem alegação de avaliação auditiva pelo agente. O usuário recebe original recortado e piano para comparar.
Velocidades derivam da ativação do modelo, não de uma recuperação validada da dinâmica original. Sem pedal, rubato novo, reconhecimento confiável da melodia ou seleção de baixo por função musical. O redutor pode descartar notas importantes; prioridade de voz mais aguda não identifica necessariamente a melodia. Fluxo real demonstrado, qualidade musical ainda pendente. Não treinou modelo ou criou arranjador aprovado.

## Próximo bloco recomendado
Receber avaliação auditiva do usuário sobre o trecho: reconhecimento da melodia, notas estranhas, acompanhamento e timbre. Escolher um defeito concreto e testar uma única intervenção com comparação A/B, preservando este baseline. Não avançar à evolução numérica como se a transcrição já fosse confiável. Integração ao site, análise integral, biblioteca e URLs seguem no plano.
