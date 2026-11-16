# Recuperação verificada de candidato — 4.8

API: GET /api/sessions/{id}/generations/{generation}/candidates/{candidate_id}/midi. Retorna MIDI binário como anexo, sem cache HTTP. Utiliza source.mid na pasta da sessão (incluído pela restauração do bloco 4.5). Se a fonte não estiver ali, o agente deve recuperar o arquivo original e conferir seu hash; não se escolhe outra música automaticamente. Candidato/geração inexistentes: 404; fonte, código ou proposta incompatíveis: 409.

CLI operada pelo agente:
```sh
.venv/bin/python scripts/recover_candidate.py --session data/session-restored-4-5 --generation 4 --candidate ID_SALVO --output data/proposta.mid
```
Opcional --source caminho/original.mid para sessões cuja fonte está fora da pasta. Recusa sobrescrever o destino.

Procedimento: validar cadeia completa; recuperar configuração e resultado do candidato; conferir código musical e SHA-256 da fonte; reduzir somente esse candidato; serializar MIDI e comparar SHA-256 com midi_sha256 registrado na avaliação. Entrega somente quando há identidade exata. Não precisa da referência para reconstrução, não recalcula score e não modifica checkpoint ou arranjador. Não é aprovação de modelo; não certifica alinhamento/transcrição. Diagnóstico pode ser reconstruído para inspeção sem ser promovido a treinamento.

114 testes passaram: igualdade de bytes com hash salvo, entrega HTTP, ausência/alteração/link na fonte, candidato/geração inexistentes, código diferente e saída divergente. Teste na sessão restaurada real de desenvolvimento, geração 4, também recuperou a proposta com hash idêntico. Esses dados são de exemplo controlado, não evidência de melhoria auditiva em Tifa.

Limites herdados: 201 checkpoints, 64 MiB de histórico, fonte MIDI até 5 MiB. Não há renderização nem player neste bloco. MIDI é a representação interna a ser enviada ao piano virtual; o objetivo final continua sendo entrada e saída em áudio. A próxima integração deve renderizar o MIDI verificado diretamente, sem submetê-lo novamente ao redutor baseline do endpoint experimental existente, pois isso poderia mudar a proposta escolhida.
