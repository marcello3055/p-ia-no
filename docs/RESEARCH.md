# Pesquisa técnica objetiva
Fontes oficiais consultadas em 14/11/2026. Pesquisa documental, sem downloads de modelos ou benchmarks musicais.

| Tecnologia | Decisão e limites | Recursos/licença |
|---|---|---|
| Basic Pitch | Primeiro candidato leve para testar áudio de instrumento isolado; não assumir transcrição correta de orquestra | Código Apache-2.0. Avaliar inferência em CPU; compatibilidade de runtime/modelo será testada em ambiente isolado |
| MT3 | Alternativa experimental multitrilha; usa T5X; documentação diz que treinamento não é facilmente suportado | Código Apache-2.0; prever experimento com GPU, sem afirmar requisito exato de VRAM antes de benchmark; verificar condições dos checkpoints |
| Demucs | Separação opcional, não transcrição. Fontes convencionais não equivalem a famílias completas de orquestra | MIT; repositório original arquivado. CPU possível, GPU deve ser avaliada para desempenho; não adotar como dependência obrigatória |
| librosa DTW | Baseline para alinhamento de representações, incluindo subsequências | CPU; custo cresce com tamanho das sequências. Reduzir resolução/segmentar; repetições não ficam resolvidas automaticamente |
| Mido / pretty_midi | Candidatos para leitura/escrita MIDI nas próximas etapas | Verificar releases, licenças e fixar versões na etapa de adoção |
| FluidSynth | Renderizador SF2/SF3; apropriado para avaliação inicial de piano em CPU | Engine separado da licença do banco de amostras. Auditar versão/licença e banco antes de redistribuir |
| Salamander Grand Piano | Candidato de amostras, não integrado | Versão consultada é SFZ com extensões ARIA; não carregar diretamente no FluidSynth. Compatibilidade e licença do pacote exato precisam ser validadas. Alternativa: motor SFZ compatível ou banco SF2 autorizado |

Fontes:
- https://github.com/spotify/basic-pitch
- https://basicpitch.spotify.com/about
- https://github.com/magenta/mt3
- https://github.com/magenta/mt3/blob/main/README.md
- https://github.com/facebookresearch/demucs
- https://librosa.org/doc/main/_modules/librosa/sequence.html
- https://www.fluidsynth.org/
- https://github.com/sfzinstruments/SalamanderGrandPiano

Risco principal: extrair corretamente melodia e harmonia de gravação orquestral densa. Separação, transcrição e redução são problemas distintos. Nenhuma destas ferramentas isoladamente entrega o produto final. Testar primeiro pipeline simbólico controlado, depois adicionar áudio em adaptadores substituíveis.

Critérios futuros de escolha: precisão em trechos autorizados representativos, latência, RAM/VRAM, licença dos pesos, manutenção e qualidade auditiva. Não escolher pelo tamanho do modelo ou popularidade apenas.

## Ensaio CPU em 15/11/2026
Basic Pitch 0.4.0/ONNX executado em ambiente separado Python 3.12; necessário contornar dependência declarada de TensorFlow incompatível e fixar setuptools para resampy. Três MP3s sintéticos transcritos de verdade. Mistura flauta/cordas: 23 correspondências em 24 notas esperadas, mas 46 estimadas; precisão 0,5 e F1 0,657 para altura/ataque. Não validado em orquestra real. Receita, dependências e dados completos: experiments/README.md e experiments/audio-probe-results.json. Mantém decisão experimental, sem adotar como transcritor definitivo ou conectar ao produto.
