# Progresso — Bloco 4.13 concluído
17/11/2026. Anterior remoto c924753d9c393f13aaf89ba8c91d903c54d7460c. O commit deste documento identifica o checkpoint atual.

Piloto evolutivo REAL sobre transcrições em cache de Tifa: 100 candidatos × 4 populações (inicial + 3 gerações), 400 posições avaliadas. Referência é o piano-objetivo informado; alinhamento provisório registrado. Código novo experiments/pilot_audio_pair.py, motor/API/frontend preservados.

Inicial 83 notas, score 0,125530524. Melhor 56 notas, score 0,127808756; melhor já encontrado na população inicial, sem aumento de score nas gerações seguintes. Não afirmar aprendizado ou melhoria auditiva. Ambos MP3s gerados, 28,5 s. Avaliador padrão usa 50 ms (não 200 ms do diagnóstico anterior); duração zerou. Limitações em docs/PILOT_4_13.md.

Testado: execução, quatro populações distintas, reprodução exata dos candidatos, retomada com mesmo hash, exportação/restauração de backup, decodificação MP3, opt-in e recusa de sobrescrita. Sem GPU/instalação/gasto/transcrição nova. Checkpoint privado b13aefe097b635ce90c2f47fb9c680d272f7e3cdad9bdd55ecb7f6461a1f0dab.

## Próximo 4.14 (aguardar autorização)
Preferência auditiva entre inicial/melhor; configurar e persistir tolerâncias do avaliador nas sessões com compatibilidade, visando próximo piloto curto. Sem nova sequência de auditorias prévias. Biblioteca de arranjadores aprovados e treinamento com MP3 pela interface permanecem pendentes.

## Artefatos persistentes
Backup privado P-IA-NO_piloto_4-13.zip: libfile_907b506dc950819197873da47d5fa161. Áudio inicial: libfile_9ec07407af688191a5f0462390b97fbb. Melhor candidato: libfile_2c6ce048d634819193cfae600c5fc44b. Gravação confirmada nos três itens.

Finalização retomada em 21/11/2026: sem repetir treinamento ou renderização; conclusão do versionamento e entrega dos áudios já preservados.
