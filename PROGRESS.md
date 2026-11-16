# Progresso — Bloco 4.1
Data: 16/11/2026. Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: 96db664261415e44b391f70ad1fda85a81f79fb5 (MP3-2b).
O commit deste documento é o checkpoint 4.1.

## Direção confirmada
Usuário avaliou melodia do trecho Tifa como 7/10, reconhecível com notas extras, suficiente para prova de conceito. Determinou avançar à Etapa 4 sem refinar essas notas agora. Avaliação humana não equivale a acurácia/generalização nem aprovação de modelo definitivo. Baseline MP3 permanece preservado; comparação A/B antes proposta foi adiada.

## Implementado
População inicial de 100 candidatos por padrão, configurável 1–390 no espaço inicial. Variam divisão de mãos, capacidade simultânea e alcance. Baseline fixo, semente local, IDs derivados de parâmetros e manifesto completo validado/recarregável. Uma entrada simbólica compartilhada; cada candidato produz MIDI ou falha explicada. Contagem de saídas musicais distintas. Nenhuma transcrição repetida, renderização em massa, nova dependência, GPU ou custo.

## Testado
76 testes passaram (71 anteriores + 5 novos). Cobrem configurações únicas/seed, limites/adulteração, fonte imutável, 100 MIDIs válidos, duplicatas musicais, falhas individuais, replay e não sobrescrita. CLI adicional em fonte sintética de 40 notas: 100 candidatos, 100 saídas geradas, zero falhas, 4 saídas musicais distintas. Não significa 100 músicas diferentes. Checkpoint/whitespace verificados; frontend não alterado, build/navegador não repetidos.

## Limites
Geração inicial 0, sem fitness/ranking/seleção/mutação/recombinação. Escores nulos e evaluated=0. Nenhum aprendizado ou melhora alegados. Três parâmetros iniciais, não todas as estratégias do objetivo final; espaço será ampliado conforme necessário. Instrumentação/transcrição/expressividade ainda experimentais. Manifestos/MIDIs de execução ficam em data/, fora do Git e fora do backup web; CLI reproduz sem sobrescrever. Sem painel da população nesta etapa.

## Próximo bloco recomendado — 4.2 (aguardar autorização)
Integrar avaliador simbólico existente à população, com referência controlada, escores explicáveis e ranking registrado. Depois, em outros blocos, seleção/reprodução e checkpoints de gerações. Não retomar refinamento isolado da transcrição neste momento. Planejamento de URLs e demais requisitos preservados.
