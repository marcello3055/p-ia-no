# Progresso — Bloco 1.1
Data: 14/11/2026. Repositório privado: https://github.com/marcello3055/p-ia-no
Checkpoint remoto anterior: c5680d23a4a4376db726ef3476d9ba63b060a2ae.
O commit que contém este documento é o checkpoint do Bloco 1.1.

## Implementado
- Três abas, roles ARIA, navegação por clique e setas/Home/End.
- Seletores e players locais para orquestra, referência e música inédita.
- Object URLs liberadas na substituição/remoção; arquivos preservados entre abas.
- Pausa na troca de abas ou ao iniciar outro player.
- Limites de formato/tamanho, mensagens para arquivos vazios, inválidos ou indecodificáveis.
- Aviso de ausência de persistência e biblioteca de modelos vazia verdadeira.
- Adaptador de preview temporário scripts/preview.py. Nenhuma dependência nova.

## Testes efetivamente executados
- PASS: build TypeScript/Vite, 2 testes API, smoke HTTP para API/HTML/assets e check_checkpoint.py.
- PASS Chrome desktop: três abas; ArrowLeft; WAV sintético de 12 s carregado (readyState 4); play confirmou paused=false; troca de aba confirmou paused=true; retorno preservou arquivo; remoção confirmada.
- PASS Chrome: .txt rejeitado; .wav danificado mostrou erro de reprodução; botão de conexão funcionou.
- Inspeção visual desktop realizada. Não houve avaliação auditiva humana/musical: trata-se de tom sintético.
- Android real e viewport móvel NÃO testados. CSS responsivo implementado.
- MP3/FLAC, arquivo vazio/grande e pausa entre dois players implementados, mas não exercitados separadamente no navegador neste bloco.

## Limites
Sem upload ao servidor, persistência musical, autenticação, transcrição, treinamento ou geração. Sem URL pública permanente; preview é temporário. Nenhum serviço pago ativado. Dados sintéticos de teste fora do Git.
GitHub é a fonte principal. Commits remotos pela integração preservam main; histórico Git local tem SHAs próprios. Não fazer force-push. Ler README, ARCHITECTURE e TODO antes de retomar.

## Próximo bloco — 1.2 (aguardar autorização)
Upload validado e limitado na API, SQLite e arquivos fora do Git para desenvolvimento; registro/listagem de pares e reprodução após reinício do processo. Não confundir persistência local com durabilidade após perda do ambiente temporário. Armazenamento gratuito externo e backup precisam ser definidos antes do uso permanente. Autenticação antes de exposição pública. Sem IA.
