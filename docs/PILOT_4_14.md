# Bloco 4.14 — tolerâncias persistentes e feedback humano
21/11/2026

## Implementação
run_session recebe evaluation_config opcional. Sessões novas usam esquema 2 e salvam a configuração completa no session.json; retomadas sem argumento reutilizam a configuração, mudança explícita é recusada. Cada ranking precisa corresponder à configuração salva. CLI aceita --evaluation-config com JSON. Sem configuração, comportamento numérico padrão preservado. Exportação/restauração existente funciona com esquema 2 e foi testada.

Compatibilidade: leitura do histórico anterior preservada; esquema 1 aceita somente tolerâncias padrão. A verificação de versão do código continua estrita: sessões criadas antes desta mudança exigem o código original para retomada, restauração e recuperação de MIDI. Para o piloto 4.13, usar checkout 28fcb5da2d4fb518e6794187d37dc6cad27fec04. Nenhuma sessão antiga foi migrada ou alterada. MP3s já salvos continuam disponíveis.

Feedback em HUMAN_FEEDBACK.json: preferência leve pelo candidato 56 notas, por limpeza e menos sobras; melodia reconhecível nos dois. Isso não é aprovação de arranjador nem autorização para recompensa indiscriminada de poucas notas. Nenhum peso alterado automaticamente.

## Piloto controlado
Mesmos inputs simbólicos, semente 0, mapa provisório e quatro pesos do bloco anterior. Única alteração na avaliação: unidade segundos, tolerâncias absolutas início/duração 200 ms, relativa duração 20%. 100 candidatos na população inicial e em três gerações seguintes: 400 posições, não necessariamente propostas distintas. Referência continua piano-objetivo; nenhuma transcrição nova.

Resultado: score 0,212052307 em todas as gerações, melhor igual ao arranjo inicial de 83 notas (MIDI e MP3 idênticos por hash). Não houve melhoria evolutiva. Este score NÃO deve ser comparado ao 0,1278 do piloto anterior como ganho, pois as tolerâncias mudaram. A escolha voltou ao candidato menos preferido pelo usuário. Aumentar tolerância isoladamente não resolveu a preferência musical. Não pedir ao usuário que escute de novo um arquivo idêntico.

## Verificação
125 testes passaram na suíte completa. Testes adicionados cobrem persistência, retomada, recusa de mudança de configuração, rejeição de NaN antes de criar sessão, mudança efetiva da correspondência por tolerância, backup/restauração. Piloto real concluído, retomada sem recomputação e restauração do ZIP com mesmo hash 218f362d28e447af0e3c67cf927a8a7eb93827f1877f595de67e92acec26385e. Código não relaxa verificação de integridade antiga.

## Próximo 4.15
Ajuste pequeno do avaliador para seleção de notas: investigar penalização de notas sem suporte da referência com proteção da linha melódica, usando a preferência registrada como caso de teste (não como prova de generalização). Comparar candidatos já disponíveis antes de executar mais gerações. Não repetir auditorias de alinhamento. UI para iniciar treinamento MP3 e arranjadores aprovados ainda pendentes.
