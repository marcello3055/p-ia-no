# Importação por URL — requisito aprovado, ainda não implementado
Registrado em 15/11/2026. Complementa a arquitetura e os requisitos existentes; não substitui upload, armazenamento, treinamento, biblioteca de arranjadores ou processamento em nuvem. Somente planejamento neste checkpoint.

## Experiência prevista
No Treinamento, Música-base e Música-objetivo terão seletores independentes: Enviar arquivo de áudio ou Informar URL do YouTube. Aceitar arquivo/arquivo, arquivo/URL, URL/arquivo e URL/URL. No Estúdio, oferecer as mesmas alternativas para a música orquestral inédita. Aceitar também URLs diretas MP3/WAV/FLAC quando a origem permitir acesso e processamento.

Para YouTube: validar endereço, identificar vídeo e consultar metadados disponíveis por meios autorizados. Exibir título, duração e player incorporado quando disponíveis/permitidos. Dados indisponíveis devem ser explicitamente indicados, sem inventar duração ou título. Vídeo privado, removido, indisponível ou com incorporação desabilitada deve produzir estado claro e preservar a referência.
Salvar URL como referência permanente do exemplo, incluindo identificador/canonicalização e metadados já obtidos. Referência permanente significa registro durável no projeto, não garantia de disponibilidade futura do vídeo. Não confundir player incorporado ou metadados recuperados com acesso ao áudio para análise.

Verificar separadamente se existe meio autorizado de obter o áudio para processamento. Se não houver, solicitar arquivo correspondente e associá-lo ao mesmo exemplo, preservando URL, título e demais metadados. O registro pode permanecer incompleto; só iniciar análise/treinamento quando os áudios exigidos estiverem disponíveis. No Estúdio aplicar a mesma regra antes de gerar o arranjo.

## Modelo de dados proposto (migração futura)
Adicionar referência de origem aos registros existentes: tipo de origem, URL, identificador do vídeo quando aplicável, título/duração conhecidos, data e fonte dos metadados, estado do acesso ao áudio e vínculo opcional com o arquivo armazenado. Preservar o identificador do exemplo ao anexar arquivo posteriormente. Guardar origem e meio autorizado utilizado; URL isolada não comprova autorização. Incluir referências/metadados no backup e restauração quando implementados. Não alterar exemplos locais existentes durante migração.
Estados previstos: validando URL; referência identificada; metadados parciais/indisponíveis; aguardando arquivo; importando áudio autorizado; pronto para análise; erro com opção de correção. Estados de metadados, incorporação e áudio são independentes.

## Obtenção e segurança — etapa posterior
Pesquisar documentação oficial e condições vigentes no momento da implementação. Escolher apenas mecanismos autorizados, gratuitos e compatíveis com o requisito de ferramentas livres; não assumir que exista API gratuita de download de áudio do YouTube. Não usar extração incompatível com condições da origem, contornar autenticação/restrições ou contratar serviços. Incorporação/serviço YouTube é integração externa opcional solicitada, não dependência paga do motor musical.
Para URLs diretas: verificar permissão de acesso/processamento, formato real, limites de tamanho/duração e erros de download. Validação de extensão sozinha é insuficiente. Downloads no backend devem restringir esquemas HTTP(S), bloquear destinos locais/privados e revalidar redirecionamentos/DNS para evitar acesso indevido à rede do servidor. Não registrar credenciais ou tokens de URLs em logs/Git. Tratar URLs assinadas como temporárias, não referências públicas permanentes.

## Cronograma incremental
- URL-1, próximo bloco dedicado de interface após a tarefa prioritária em curso: campos independentes, validação/identificação, metadados por mecanismo autorizado, incorporação permitida e persistência da referência. Tratar ausência de acesso ao áudio com solicitação de arquivo sem perda de dados. Revisar migração e backup neste bloco; subdividir se necessário.
- URL-2, etapa de aquisição/análise de áudio: obtenção autorizada de arquivos diretos e integração ao processamento/cache existente. Para YouTube, integrar apenas se houver meio autorizado efetivamente disponível; caso contrário manter referência + arquivo fornecido.
- URL-3, integração ao Estúdio definitivo/histórico: reutilização da mesma abstração, rastreabilidade e tratamento de indisponibilidade posterior.
Os campos e identificação no Estúdio também entram no URL-1; URL-3 é integração ao fluxo final, não adiamento desses campos. Não interromper a prova de viabilidade MP3 prioritária para implementar URLs. Cada incremento exige autorização, testes e checkpoint próprios.

## Critérios de aceitação futuros
1. Quatro combinações de origem nos pares; Estúdio aceita arquivo ou URL independentemente.
2. URL inválida é recusada; falha de metadados/embed não apaga dados já preenchidos.
3. Referência persiste após recarregar/reiniciar e após backup/restauração.
4. Anexar arquivo a referência existente preserva metadados e identificação do exemplo.
5. Player YouTube nunca é apresentado como áudio já disponível ao analisador.
6. Sem acesso autorizado, análise não começa; solicitação de arquivo é clara.
7. URL direta autorizada passa pelas mesmas validações de mídia e limites do upload; destino inseguro/redirecionamento indevido é bloqueado.
8. Nenhuma regressão nos uploads locais, pares existentes ou versões aprovadas de arranjadores.
