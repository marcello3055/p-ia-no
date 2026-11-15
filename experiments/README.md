# Prova de viabilidade MP3 — experimento isolado
Não integra a API, a interface ou o treinamento. Não use este script como serviço de upload público. Opera exclusivamente em exemplos sintéticos pequenos gerados pelo próprio script, sem músicas privadas.

## Reprodução pelo agente
```sh
bash experiments/setup_audio.sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv-audio/bin/python experiments/audio_probe.py --output-dir data/audio-probe-novo
```
Requer biblioteca FluidSynth, TimGM6mb e FFmpeg documentados no renderizador. Saída deve ser pasta nova. Reutilizar resultados existentes; não repetir inferência para simples leitura de métricas. Dados binários ficam em data/, fora do Git; receita, versões e relatório textual controlado ficam no repositório.

## Dependências
Basic Pitch 0.4.0 (Spotify), modelo ONNX ICASSP 2022 incluído no pacote oficial PyPI, licença Apache-2.0 do pacote; não redistribuímos pesos no Git. Documentação: https://github.com/spotify/basic-pitch e https://github.com/spotify/basic-pitch/blob/main/LICENSE . ONNX Runtime CPU (MIT), dependências numéricas livres. Banco TimGM6mb GPL-2 já documentado; amostras não copiadas ao repositório.
Instalação isolada com versões fixas e `--no-deps`: os metadados upstream exigem TensorFlow <2.15.1 no Python >=3.11, incompatível com Python 3.12 disponível. Usamos a alternativa ONNX fornecida upstream; isso não significa suporte oficial upstream ao Python 3.12. `uv pip check` pode apontar TensorFlow ausente por esse motivo deliberado. Setuptools 80.9.0 fornece pkg_resources exigido pelo resampy 0.4.2; foi detectada falha de importação antes de acrescentá-lo. Ambiente principal não alterado. Lock contém versões exatas, ainda sem hashes de todas as wheels; hashes do modelo e banco registrados no relatório.

## Desenho e limites
Três MP3s locais de notas conhecidas: melodia de piano, acordes de piano, mistura de flauta e cordas sintéticas. Dois casos de piano são controles; a mistura não equivale a orquestra real. Sem ajuste de thresholds, treinamento, separação de fontes, reconhecimento de melodia ou alinhamento automático.
Modelo pré-treinado reutilizado, execução CPU. Mantém saídas brutas, ativações e eventos estimados para inspeção. Valores de ativação NÃO são probabilidades calibradas. Avaliação compara alturas exatas e ataques com tolerância de 100 ms, duração com máximo de 150 ms ou 20% da duração de referência. Pitch bends ignorados explicitamente. A duração acústica pode diferir do note-off, especialmente em piano, portanto a métrica de duração não mede sozinha qualidade perceptual.
Tempo de inferência inclui pré/pós-processamento; primeiro caso pode pagar compilação JIT e importações tardias. Pico RSS é do processo completo, não alocação exclusiva do modelo. Não extrapolar desempenho para músicas longas ou celular. Nenhum gasto/serviço externo de inferência. Basic Pitch é descrito pelo próprio projeto como mais adequado a um instrumento por vez; resultados deste ensaio não comprovam generalização orquestral.

## Resultado medido em 15/11/2026
| Caso sintético | Notas esperadas | Estimadas | Correspondências altura+ataque | F1 altura+ataque | F1 incluindo duração |
|---|---:|---:|---:|---:|---:|
| Melodia de piano | 8 | 12 | 8 | 0,800 | 0,000 |
| Acordes de piano | 16 | 19 | 16 | 0,914 | 0,571 |
| Flauta + cordas | 24 | 46 | 23 | 0,657 | 0,171 |

São métricas de correspondência neste ensaio, não porcentagens de qualidade musical. Na mistura, recall alto coexistiu com precisão de apenas 0,5: muitas notas extras. Durações foram especialmente frágeis. Nenhum threshold foi ajustado após observar resultados.
Pico RSS do processo: 423,64 MiB. Primeiro caso: 11,54 s; casos posteriores: ~0,10–0,11 s cada (áudios curtos de cerca de 7 s). Não generalizar velocidade ou memória para orquestra/gravações longas. Relatório integral: audio-probe-results.json; resultados intermediários em data/audio-probe-02 no ambiente de trabalho.
Conclusão: inferência MP3 em CPU é viável neste ambiente; Basic Pitch isoladamente não está validado como transcritor orquestral. Próximo teste deve usar um trecho real autorizado, com escuta e inspeção das notas extras/durações, antes de integrar ao site ou iniciar otimização evolutiva sobre transcrições incertas.

## Preparação para gravação real — MP3-2a
O agente pode agora preparar um trecho de arquivo completo com `scripts/prepare_audio_clip.py`, no ambiente principal: validação, recorte mono/22.050 Hz e cache verificável. Consulte docs/AUDIO_CLIPS.md. Não houve novo ensaio de transcrição real neste bloco; o arquivo orquestral ainda não foi fornecido. O script audio_probe.py continua restrito às três fontes sintéticas.
