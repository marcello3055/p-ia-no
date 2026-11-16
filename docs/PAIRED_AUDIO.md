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

## Correção pelo usuário — 4.2b, 16/11/2026
O usuário REJEITOU a correspondência anterior (piano 4,83–18,20 s). As pontuações 0,173571/0,183768 acima são histórico inválido para este par e NÃO devem orientar seleção. Indicou OST desde 24–25 s até 50 s e piano de 20 s ao fim do segundo 37. Adotados 24,5–50 s e 20–38 s; 24,5 é aproximação explícita, não âncora exata medida.

experiments/anchored_alignment.py prepara ambos os trechos e aplica DTW ponta a ponta, sem busca global. Corredor de 15% no progresso normalizado restringe deslocamentos internos; hop reduzido para 1024/11025 ≈92,9 ms. Extremos do mapa fixados exatamente. Dentro do corredor ainda existem repetições e patamares; custo não indica confiança. Regiões confirmadas pelo usuário, correspondência nota a nota não confirmada. Desvio máximo normalizado medido 0,14971, próximo à borda; manter cautela quanto ao caminho interno. Sem ajuste para maximizar score de candidato.

Nova inferência OST necessária por ampliação: 126 notas estimadas; baseline reduz para 83 (30 descartes por simultaneidade, 13 alcance). Referência piano: 79 notas estimadas/mapeadas, zero fora da janela/colapsadas/truncadas. Com as mesmas regras de pontuação, 100 candidatos/62 avaliações únicas; baseline e máximo empatados em 0,212052. Não comparar esse número diretamente ao diagnóstico rejeitado, pois trecho e referência mudaram. NÃO é 21,2% de precisão; não demonstrou melhoria sobre baseline nem aprendizado.

Resultados novos: data/source-corrected-01 e data/pair-corrected-01. Relatório anterior marcado rejected_by_user e motivo preservado localmente. Pacote de entrega anterior continua histórico rejeitado; pacote corrigido é a referência vigente. Original de entrada não alterado. Status novo diagnostic_only_internal_warp_unverified, training_allowed=false; nenhuma geração evolutiva realizada.

84 testes do projeto passaram. Verificação adicional, reproduzível com `.venv-audio/bin/python experiments/check_anchored_alignment.py`, testa identidade, extremos, monotonicidade, corredor e transformação de uma nota sintética. Não valida qualidade do mapa real. Próximo bloco: implementar ciclo 4.3 em exemplos simbólicos controlados; uso do par real no treinamento permanece experimental e exige tratamento explícito da incerteza temporal. Não é necessário pedir novamente ao usuário para identificar a região já indicada.
