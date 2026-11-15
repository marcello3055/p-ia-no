# Representação MIDI — Bloco 2.1

## O que funciona
`packages/music/midi.py`: read_midi(bytes) retorna Score; Score.to_dict() produz JSON schema_version 1; write_midi(score) gera um MIDI novo a partir das notas/eventos. Não é cópia dos bytes de entrada. scripts/inspect_midi.py permite ao agente gerar JSON e MIDI; não existe importador JSON nem integração com a interface nesta etapa.

Notas: trilha, canal, altura MIDI, velocity, release_velocity, início/fim em ticks e ordem dos eventos. JSON acrescenta tempos em semínimas (quarters) e segundos. source=midi; role/hand/confidence=None: não se inferem melodia, mãos ou confiança perceptual. Track_ends mantém silêncio final; events preserva controles, programas e metadados, inclusive nomes e fórmulas de compasso.

## Tempo e interpretação
Suporte a tipos 0/1 com PPQN positivo. Tempo padrão 500.000 microssegundos por semínima; mapa global de alterações integra intervalos, inclusive mudanças durante uma nota. Em conflito simultâneo, prevalece a última mensagem por ordem de trilha/evento, com aviso. A unidade quarters não equivale necessariamente à pulsação indicada pela fórmula de compasso.
Note-on com velocity zero encerra nota. Duração representa pressionamento da tecla, não cauda sonora/pedal. CC64 é preservado, sem prolongamento artificial das notas. Pitch bend é preservado com aviso: pitch continua sendo a tecla original. SysEx é omitido com aviso; eventos não são enviados a instrumentos ou hardware.

## Restrições deliberadas
Tipo 2 (trilhas assíncronas) e SMPTE recusados. Fim sem início, nota sem fim e sobreposição da mesma altura/canal na mesma trilha são recusados: não inventar pareamento/duração. Notas simultâneas em canais ou trilhas diferentes são distintas. Zero duração é aceito com ordem preservada. Não transforma orquestra em piano, não sintetiza áudio e não avalia qualidade.
Máximo 5 MiB, 128 trilhas e 100.000 eventos. Mido carrega o arquivo em memória; o limite de bytes é verificado antes. A CLI lê no máximo limite+1. Validação pós-exportação verifica pareamento após edições. Dados gerados ficam fora do Git, salvo JSON de exemplo explicitamente aprovado.

## Testes
Casos sintéticos: tempo padrão, desligamento por velocity zero, mudança de tempo dentro de nota, acordes/repetições/canais, programas/pedal/compasso/silêncio final, edição de pitch/velocity/duração, entradas inválidas e não suportadas, nota de duração zero, SysEx/pitch bend e CLI sem sobrescrita. Comparação semântica, não igualdade de bytes MIDI. Arquivos reais de usuário ainda não avaliados.

## Fonte e dependências
Mido 1.3.3 (MIT), versão e licença verificadas no pacote instalado. Documentação oficial consultada em 14/11/2026: https://mido.readthedocs.io/en/stable/files/midi.html e https://mido.readthedocs.io/en/stable/about_midi.html . A documentação stable consultada se identifica como 1.3.2; comportamento da versão instalada foi testado. Dependências fixadas com hashes no requirements.lock; sem API paga/GPU.
