# Bloco 4.17 — indicadores integrados e piloto
21/11/2026, data local.

## Implementado
Perfil opcional clean-melody-v1 no ranker e na sessão; standard continua disponível e padrão. O perfil compõe 60% da pontuação anterior (pesos finais 0,30 alturas/inícios, 0,15 duração, 0,09 classes de altura, 0,06 ataques), 30% F0,5 de correspondência (limpeza) e 10% cobertura do guia de voz superior. Constantes fixadas antes do piloto, não ajustadas após resultados. Cada parcela e contribuição aparece separadamente no relatório e na tabela da interface. Sem bloqueio por guia; guia vazio é explicitamente indisponível e contribui zero, sem renormalização oculta. Ausência de correspondência não prova nota errada.

Algoritmo de guia portado para packages/music/guide.py para integrar o motor e o hash de código. Sessões do perfil experimental usam esquema 3; perfil/tolerâncias são persistidos, retomada os reutiliza, alteração de perfil é rejeitada. CLI --ranking-profile. Backup/restauração testados. Sessões antigas não foram migradas; execução/reprodução exige seu código original, conforme política existente. Perfil standard mantém os quatro critérios numéricos anteriores.

## Piloto
Mesmas transcrições e mapa provisório de Tifa, tolerância 200 ms, seed 0. Inicial + três gerações, 100 candidatos cada, 400 posições avaliadas (incluem elites/repetições). Baseline 83 notas, score 0,195509973. Melhor inicial 0,197031970; geração 1 chega a 0,197820789, mantido nas gerações 2 e 3. Novo candidato candidate-aec146090cc9b667, 54 notas. Crescimento numérico dentro do mesmo perfil é pequeno, não demonstra melhora auditiva.

Comparado ao baseline, limpeza sobe de 0,15815 para 0,18644, mas cobertura do guia cai de 5/24 para 4/24 e similaridade de classes de notas cai de 0,49888 para 0,43417. Troca entre critérios explicitada, sem alegação de melodia preservada com certeza. Novo MIDI tem hash diferente do preferido humano 4.13 de 56 notas. MP3 gerado com mesmo piano TimGM6mb, 28,5 s. Escuta humana pendente. Nenhuma generalização ou arranjador aprovado.

## Testado e salvo
Suíte existente: 134 testes passaram após mudança do motor. Três testes novos passaram (contribuições somam score, guia vazio sem cobertura inventada, retomada/perfil imutável e backup). Total 137 testes executados com sucesso, em duas chamadas. Build TypeScript/Vite passou; sem nova verificação visual em Chrome neste bloco. Piloto real, recuperação exata do MIDI, retomada sem novas gerações e restauração do ZIP com hash idêntico concluídos.

MP3 libfile_5b1bcc95f5fc81918f050607f8c88bc0; backup libfile_ca84111451508191b305a537e2bb486a. Hash da sessão 10f671331bc413afd49da9c40d689f05e9951b8f4ed35de0563ce5b10cce6c10. Código/métricas no Git, áudios/checkpoints privados no pacote. Reproduzir usando experiments/pilot_audio_pair.py com os mesmos parâmetros de 4.14 e --ranking-profile clean-melody-v1, em pasta nova.

## Próximo 4.18
Registrar preferência entre novo 54 notas e anterior 56 notas. Priorizar ligação dos exemplos de áudio em cache à criação de uma sessão pelo backend, com execução curta, progresso/erro e proveniência explícita; preparar o botão de início na interface em incremento posterior. Não reabrir auditorias nem ajustar indefinidamente o avaliador a Tifa. O caminho geral de novos MP3s ainda precisa integrar análise/treinamento na aplicação; nenhum serviço pago foi usado.
