# Progresso — Bloco 4.17 concluído
21/11/2026. Remoto anterior 24e90a3e638ca5d282e1336fb4d2021d22ad6118. O commit deste documento identifica o checkpoint atual.

Perfil clean-melody-v1 integrado ao ranker/sessões/CLI, persistido esquema 3. 60% critérios anteriores + 30% limpeza F0,5 + 10% guia melódico heurístico. Sem bloqueio absoluto do guia. Tabela frontend exibe novos critérios apenas quando presentes. Standard continua padrão. Sessões anteriores preservadas e exigem checkout original para execução.

Piloto real 100 candidatos, inicial + 3 gerações: melhor inicial 0,197031970, final 0,197820789; baseline 0,195509973. Novo melhor de 54 notas, MIDI diferente do anterior de 56; limpeza maior, cobertura do guia menor que baseline (4/24 vs 5/24). Não alegar melhora auditiva. MP3 28,5s pronto, avaliação humana pendente.

134 testes existentes + 3 novos passaram; build frontend passou. Recuperação de candidato, retomada e restauração do backup verificadas. Sem transcrição nova/GPU/gasto. Método docs/PILOT_4_17.md, evidências PILOT_4_17_RESULT.json.

Artefatos: Tifa_candidato_4-17.mp3 libfile_5b1bcc95f5fc81918f050607f8c88bc0; P-IA-NO_piloto_4-17.zip libfile_ca84111451508191b305a537e2bb486a. Hash sessão 10f671331bc413afd49da9c40d689f05e9951b8f4ed35de0563ce5b10cce6c10. Backup4.14 libfile_111a013223488191b07808261aa9bb68; backup4.13 libfile_907b506dc950819197873da47d5fa161.

## Próximo bloco 4.18 (aguardar autorização)
Feedback auditivo 54 vs 56 notas. Ligar exemplos de áudio com análise em cache à criação de sessão no backend, execução curta/progresso/erros/proveniência; botão de iniciar no frontend em incremento posterior. Parar sequência de calibrações em Tifa. Biblioteca de arranjadores aprovados e fluxo completo de novos MP3s continuam pendentes.
