# Progresso — Bloco 4.14 concluído
21/11/2026. Checkpoint remoto anterior 28fcb5da2d4fb518e6794187d37dc6cad27fec04. O commit deste documento identifica o atual.

Feedback humano registrado: segundo candidato 4.13 ligeiramente melhor, menos sobras; melodia boa/reconhecível nos dois. Sem aprovação permanente de arranjador nem atualização automática de pesos.

Implementadas tolerâncias configuráveis, persistentes e imutáveis dentro da sessão; CLI JSON, esquema 2. Retomada e backup reutilizam configuração. Histórico antigo preservado; para executar sessões antigas usar seu checkout original (4.13: 28fcb5d), pois hash de código não é contornado.

Executado piloto 4.14: 100 candidatos, inicial + 3 gerações, tolerância 200 ms, mesmos dados/cache. Melhor = inicial de 83 notas, score 0,212052307 constante; MIDI/MP3 idênticos ao inicial anterior. Sem melhoria. Não apresentar aumento de score por mudança de tolerância como evolução musical. Não solicitar nova escuta de áudio idêntico.

125 testes passaram. Piloto, retomada e restauração do backup concluídos. Sem instalação, GPU, despesa ou nova transcrição. Evidências docs/PILOT_4_14.md e PILOT_4_14_RESULT.json.

Backup privado P-IA-NO_piloto_4-14.zip: libfile_111a013223488191b07808261aa9bb68. Checkpoint interno 218f362d28e447af0e3c67cf927a8a7eb93827f1877f595de67e92acec26385e. Pacote antigo permanece libfile_907b506dc950819197873da47d5fa161.

## Próximo bloco 4.15 — aguardar autorização
Ajuste limitado do avaliador para notas sem suporte com proteção melódica, confrontar com preferência humana usando candidatos em cache. Não aumentar gerações cegamente nem reabrir auditorias. Fluxo MP3 na interface e biblioteca de arranjadores aprovados continuam pendentes.
