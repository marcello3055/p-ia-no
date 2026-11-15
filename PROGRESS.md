# Progresso — Bloco 2.2
Data: 14/11/2026 (fuso do usuário). Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: e86ae6b8e02f2fbbb71013f493a39a57963d4f4d.
O commit que contém este documento é o checkpoint 2.2.

## Implementado
- Avaliador entre dois Scores/MIDIs: inventário de alturas, altura+início e altura+início+duração.
- Precisão, recall, F1, erros médios, contagens, pares e índices sem correspondência.
- Pareamento cronológico um a um, sem reutilizar notas; tolerâncias configuráveis e unidades quarters/seconds.
- Filtro de percussão padrão; configurações/avisos explícitos; referência vazia recusada.
- CLI de relatório JSON sem sobrescrever destinos. Regras em docs/EVALUATOR.md.

## Testes
- 38 testes aprovados: 27 anteriores + 11 do avaliador.
- Casos controlados comprovam identidade, perda/excesso de notas, altura errada, duplicações, início/duração, limites, andamento/PPQN, entradas vazias e CLI.
- Erro de duração não apaga resultado de correspondência de altura/início; erros médios não viram zero na ausência de pares.
- Sem nova dependência, renderização, uso de GPU ou serviço pago.

## Limites
Avaliador ainda interno, não integrado à interface; MIDI não pode ser enviado pelo site. Não mede qualidade artística, harmonia funcional, motivos, mãos, tocabilidade ou expressão. Sem alinhamento de introduções/repetições/rubato. Sem treinamento ou alegação de generalização. Só testes sintéticos. Hospedagem, autenticação, backup automático e Android continuam pendentes.
GitHub é a fonte principal; não versionar áudios, DBs ou MIDIs privados. Histórico local e remoto têm SHAs próprios; publicar pela integração sobre SHA observado, sem force-push.

## Próximo bloco recomendado — 2.3 (aguardar autorização)
Integrar a comparação MIDI à interface: selecionar referência/candidato, mostrar métricas com explicações e exportar relatório, com limites no servidor. Sem treinamento ou transcrição de MP3. Não executar nesta sessão.
