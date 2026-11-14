# Progresso — Bloco 1.2
Data: 14/11/2026. Repositório privado: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: 362524463116e8ff1e136916c0f5339cc4887a81.
O commit contendo este documento é o checkpoint 1.2.

## Implementado
- Upload em streaming, validação por ffprobe, MP3/WAV/FLAC, 100 MiB/arquivo, 30 min e quota 1 GiB.
- SQLite e data/audio fora do Git, nomes internos UUID e deduplicação SHA-256.
- Criação/listagem de pares nomeados e áudios; reprodução com suporte a Range.
- Interface Salvar, progresso de envio/validação, erros, Atualizar lista e players dos arquivos salvos.
- Seleção permanece local até clicar Salvar; aviso explícito de durabilidade limitada.

## Evidências
- Build TypeScript/Vite aprovado.
- 8 testes API aprovados: saúde, endpoint musical inexistente, bytes/pares reabertos, Range, duplicação, entrada inválida/traversal, quota/limite em streaming, arquivo ausente e referências inválidas.
- test_restart.py: servidor real encerrado e recriado; par recuperado e ambos os áudios byte a byte iguais.
- Smoke HTTP: saúde, HTML e assets servidos corretamente.
- Chrome desktop: par sintético salvo pela interface, listagem confirmada após reload, reprodução HTTP iniciou (paused=false, duração 12 s); aba Arranjar listou áudio salvo.
- Dados sintéticos de QA fora do Git. Nenhuma música do usuário usada. Par sintético não é evidência de aprendizado.
- MP3/FLAC e Android real ainda não exercitados neste bloco; áudio de teste WAV sintético. Queda de energia/interrupção abrupta não testada.

## Limitações
Sem backup externo, hospedagem permanente, autenticação, múltiplos workers ou múltiplos usuários. Arquivos sobrevivem a reinício normal, NÃO ao descarte do ambiente. Pode haver arquivos órfãos após encerramento abrupto; recuperação automática pendente. Atualizar lista busca novos dados entre abas.
Sem transcrição, evolução, MIDI, modelos aprovados ou geração de piano. Nenhum recurso tarifado ativado e nenhuma dependência nova instalada.
GitHub é a fonte principal do código. Dados e DB não enviados. Histórico local difere dos SHAs remotos; publicar pela integração sobre main observado, sem force-push.

## Próximo bloco — 1.3 (aguardar autorização)
Backup e restauração verificável dos pares/áudios, com hashes e validação de caminhos, para recuperação em ambiente novo; esclarecer a escolha de armazenamento gratuito durável antes de receber músicas reais. Sem IA ou hospedagem pública. Não iniciar outra etapa nesta sessão.
