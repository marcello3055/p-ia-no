# Progresso — Bloco 2.1
Data: 14/11/2026 (fuso do usuário). Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: c2137709e1cd315c859fc6b51257971619058b6d.
O commit que contém este documento é o checkpoint 2.1.

## Implementado
- Mido 1.3.3 e packaging 26.3 instalados, licenças verificadas, lockfile com hashes; nenhuma atualização dos demais pacotes.
- Núcleo MIDI tipo 0/1: Score, Note e Event, trilhas/canais, alturas, intensidades, inícios/fins e conversão ticks/semínimas/segundos.
- Mapa de andamento global; preservação de controles, programas e metadados. Pedal não confundido com duração da tecla.
- Exportação real a partir da representação, incluindo edições de notas.
- CLI de inspeção/reexportação sem sobrescrever destinos. Sem integração MIDI no site ainda.

## Verificações
- 27 testes aprovados: 18 anteriores e 9 novos de MIDI.
- Casos MIDI sintéticos: acordes, simultaneidade, repetição, velocity zero, tempo padrão, mudança de tempo dentro de nota, canais/trilhas, pedal/compasso/programa, silêncio final, zero duração, edição simbólica e reexportação, entradas inválidas e CLI.
- Arquivos com notas sem fim ou pareamento ambíguo recusados. SMPTE/tipo 2 recusados. SysEx descartado com aviso. Pitch bend preservado como evento.
- Nenhum áudio gerado ou modelo treinado. MIDI real de repertório do usuário ainda não testado. Nenhum teste visual adicional: interface não mudou.

## Limites e continuidade
Sem avaliador musical ainda; sem inferência de melodia, vozes/mãos, transcrição de MP3, redução pianística ou evolução. JSON exportado é informativo; importação JSON não implementada. Backups de dados, armazenamento local e interface dos blocos anteriores mantidos. Android, hospedagem, autenticação e backup automático continuam pendentes.
GitHub é a fonte principal do código; áudio/bancos/MIDIs gerados não versionados. Histórico remoto difere do local; usar integração sobre SHA observado, sem force-push. Sem gastos externos/GPU. Ler docs/MIDI.md para limites e testes antes de ampliar.

## Próximo bloco — 2.2 (aguardar autorização)
Avaliador inicial entre dois MIDIs com métricas explicáveis de alturas, início/duração e precisão/recall, usando exemplos controlados. Separar erro musical de diferença de andamento; não afirmar avaliação de expressividade/generalização. Não executar neste bloco.
