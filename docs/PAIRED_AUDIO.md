# Par de áudio real — diagnóstico supervisionado 4.2a
Data: 16/11/2026. Corrige a lacuna de integração: os rankings anteriores eram testes com referência MIDI sintética. Agora foi usado o MP3 de piano enviado pelo usuário, separado da OST de origem. Não é ainda avaliador supervisionado validado.

## Executado
Reutilizada transcrição da OST 30–50 s (99 notas), sem nova inferência da fonte. experiments/align_reference.py compara cromas STFT (12 classes, 11.025 Hz, n_fft 4096, hop 2048 ≈185,76 ms) com DTW por subsequência/cosseno, usando librosa 0.11.0 já instalada. Decodificação alvo limitada a 600 s, ferramenta interna para arquivos locais confiáveis. Consulta web da documentação DTW retornou 404; execução usa API instalada e teste de identidade, não suposta documentação recuperada.
Melhor caminho propôs referência entre 4,830 e 18,204 s. Custo por frame final 0,17971; alternativas de término separadas por pelo menos 10 s: 28,421 s (0,19406), 95,666 s (0,19675). Alternativas são terminais, não caminhos completos independentes. Custos próximos e representações harmônicas não bastam para declarar correspondência correta; status proposed_unverified. Não é probabilidade/confiança calibrada.

Transcrição do piano inclui 1 s de margem em cada lado. Basic Pitch/ONNX estimou 42 notas; mapeamento inverso do DTW reteve 37, excluiu 5 fora da janela e truncou 3 nas bordas. Patamares do mapa são agregados pela média do tempo da fonte antes de interpolação linear. Isso pode distorcer ataques/durações. O alvo é mapeado uma vez, independentemente dos candidatos; não realinhado para favorecer cada candidato.

## Comparação provisória
100 candidatos avaliados, 63 avaliações únicas. Pesos atuais 0,50/0,25/0,15/0,10; comparação em segundos com tolerância de início 0,2 s e duração máximo(0,2 s;20%). Baseline: 0,173571; máximo: 0,183768. NÃO interpretar como porcentagem de acerto, melhora artística ou ranking confiável. Não comparar diretamente com o ensaio sintético anterior ou 7/10 humano. Ambas as transcrições são estimativas e o alinhamento está pendente.
Relatório marca status=diagnostic_only_alignment_unverified e training_allowed=false; nenhuma reprodução/seleção executada. São flags de diagnóstico; ainda não existe consumidor evolutivo que aplique esse bloqueio, e tal consumidor deverá verificá-las.

## Arquivos e reprodução
Fonte privada: data/real-clip-01/report.json. Alinhamento: data/pair-01/alignment.json. Referência/ativações/manifesto/ranking: data/pair-01/comparison. Mídia, notas estimadas e relatórios detalhados privados fora do Git; pacote de entrega permite recuperação.
```sh
.venv-audio/bin/python experiments/align_reference.py trecho_ost.wav piano.mp3 --output data/novo/alignment.json
.venv-audio/bin/python experiments/compare_audio_pair.py piano.mp3 --source-report data/real-clip-01/report.json --alignment data/novo/alignment.json --output-dir data/novo/comparison
```
Destinos novos; hashes verificam identidade da referência e do trecho fonte. Não reexecutar inferência para apenas ler resultados. Scripts não são endpoints públicos, sem interface de alinhamento manual ainda.

## Testes e próximo passo
84 testes passaram (81 anteriores + 3 de mapeamento: deslocamento/escala, bordas/patamares, mapas inválidos). Teste adicional DTW do trecho consigo mesmo retornou identidade e custo praticamente zero: valida execução básica, NÃO a correspondência entre interpretações. Inferência real/ranking concluídos; sem avaliação auditiva automática.
Usuário deve ouvir os recortes propostos: OST 30–50 s e piano 4,83–18,20 s. Confirmar/corrigir correspondência antes de seleção evolutiva; se incorreta, escolher âncoras/trecho manual em vez de tratar métricas baixas como problema dos bots. Não retomar ajuste de notas extras isolado nem presumir generalização.
