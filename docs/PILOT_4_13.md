# Piloto real 4.13 — Tifa
17/11/2026. Reutilizados MP3s previamente transcritos: OST 24,5–50 s, piano-objetivo 20–38 s. Fonte 126 notas estimadas; referência 79 notas alinhadas. Sem nova transcrição, GPU, custo ou ajuste de redes neurais.

## Executado
População de 100, geração inicial 0 e três gerações evolutivas, semente 0; 400 posições avaliadas, incluindo repetições/elites. Cache de propostas equivalentes dentro de cada geração; não são 400 arranjos únicos. Quatro populações com hashes distintos. Seleção, mutação/recombinação e checkpoints pelo motor existente. Piloto autorizado explicitamente por opção própria; nenhum ranking diagnóstico reaproveitado ou marcado como validado. Mapa anterior mantido como hipótese provisória, porque a alternativa restrita não melhorou o diagnóstico de notas.

## Resultado
Arranjo padrão: 83 notas, score 0,125530524. Melhor escolhido: 56 notas, score 0,127808756. O melhor score já existia na geração inicial e permaneceu igual nas gerações 1–3: NÃO houve ganho evolutivo demonstrado neste piloto. Menos notas não implica melhor música. MP3/WAV de ambos renderizados diretamente dos MIDIs avaliados, 28,5 segundos cada incluindo cauda de 3 segundos; piano TimGM6mb, sem expressão nova. Sem avaliação auditiva subjetiva neste bloco.

## Avaliador usado
50% alturas/inícios (F1), 25% alturas/inícios/duração (F1), 15% classes de notas ao longo do tempo, 10% ataques. Configuração padrão da sessão: tolerância de início 0,1 semínima = 50 ms neste MIDI, duração max(50 ms,20%). É mais restrita que os 200 ms do ranking diagnóstico anterior, portanto não comparar suas pontuações diretamente. Duração zerou para os dois resultados. A métrica ainda não reconhece melodia principal nem expressividade; erro de transcrição e alinhamento pode reduzir scores. Não converter scores em percentual de fidelidade ou nota artística.

## Verificado
Execução real, recuperação dos dois candidatos com hash MIDI idêntico ao avaliado; retomada sem novas gerações com mesmo checkpoint; exportação e restauração do backup com mesmo hash; decodificação integral dos dois MP3s sem erro; recusa de execução sem opção experimental e de sobrescrita. Não repetida suíte integral pois motor/API/frontend não foram modificados. Evidências agregadas em PILOT_4_13_RESULT.json.

## Recuperação e próximo bloco
Pacote privado P-IA-NO_piloto_4-13.zip contém session-backup.zip, proveniência, resultado, entradas simbólicas/cache e MP3s. Para restaurar usar scripts/session_backup.py com o ZIP interno, mantendo pilot.json/result.json ao lado para preservar status experimental. Não é arranjador aprovado. Código no Git; notas/áudios/checkpoints detalhados fora do Git.

Próximo 4.14: registrar preferência auditiva inicial/melhor e tornar as tolerâncias do avaliador configuráveis e reproduzíveis na sessão (preservando compatibilidade), para um próximo piloto curto com tolerância adequada às transcrições. Não iniciar nova auditoria de alinhamento nem aumentar gerações cegamente. Fluxo completo de iniciar treinamento por uploads na interface continua pendente.

Comando do piloto: .venv/bin/python experiments/pilot_audio_pair.py --source-report data/source-corrected-01/report.json --pair data/pair-corrected-01 --output data/tifa-pilot-4-13 --allow-provisional-pilot
A pasta de saída deve ser nova. A execução limita-se a este par e a três gerações.
