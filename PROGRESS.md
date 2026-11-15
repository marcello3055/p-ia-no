# Progresso — Bloco 2.3
Data: 14/11/2026 (fuso do usuário). Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: 8cc7d821d60b2cd1bbad27f04e809d00039b2bd6.
O commit deste documento é o checkpoint 2.3.

## Implementado
- Painel Comparar dois MIDIs na aba Treinamento, seleção referência/candidato, tolerâncias e unidade temporal.
- Métricas explicadas, contagens, erros médios, avisos e download do relatório JSON completo.
- Resultado invalidado ao trocar arquivo/parâmetro; estado de processamento e erros.
- API binária efêmera (5 MiB/arquivo, 10 MiB total), validação de conteúdo/configuração e hashes de origem. Não salva MIDI ou relatório na biblioteca.
- Um pedido por processo; comparação em thread; nenhuma dependência nova.

## Testes
- 44 testes aprovados: 38 anteriores e 6 da API MIDI.
- Casos novos: resultado e hashes, diferenças/configuração, arquivo inválido/vazio, limites e parâmetros inválidos, tipo de conteúdo e excesso durante streaming, ausência de persistência.
- TypeScript/build Vite aprovados.
- Chrome desktop: arquivos sintéticos com uma nota diferente; exibiu 1 correspondência em 2 notas e 50% nos critérios. Download JSON concluído. Troca para MIDI inválido limpou resultado anterior e mostrou erro.
- Sem teste Android real, carga simultânea ou arquivo musical real. Não foi feita avaliação auditiva.

## Limitações
Sem alinhamento automático ou avaliação artística/harmonia funcional/tocabilidade/expressividade. Sem transcrição MP3, treinamento ou geração de áudio. Arquivos e resultados da comparação são efêmeros; baixar JSON para guardar. Dados salvos de áudio dos blocos anteriores permanecem independentes.
Sem URL pública permanente, autenticação, backup externo automático ou vários workers. Timeout do navegador não interrompe necessariamente a thread. Nenhum gasto/GPU. GitHub fonte principal; dados privados fora do Git; não force-push.

## Próximo bloco recomendado — 2.4 (aguardar autorização)
Ampliar o avaliador inicial com comparação harmônica básica (classes de altura) e padrões rítmicos controlados, separando essas métricas de qualidade artística. Não iniciar motor evolutivo ou transcrição. Publicação e validação Android seguem pendentes.
