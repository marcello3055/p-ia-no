# Progresso — Bloco 4.3, primeiro ciclo evolutivo
Data: 16/11/2026. Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior remoto: acc30c14d2daedc61930dd21cac2ea89a3e60736 (4.2b, confirmado).
O commit deste documento é o checkpoint 4.3.

## Implementado
Seleção de elites, recombinação, mutação, imigrantes e preservação do baseline. População configurável, parâmetros únicos, limites de execução e ancestralidade reproduzível. Ranking vinculado à população/geração por hash. Recusa de diagnósticos/rejeitados. CLI grava populações e rankings 0/1 sem sobrescrever destino existente. Docs/EVOLUTION.md descreve operação e limites.

## Verificação
89 testes passaram. CLI real em exemplo MIDI controlado: 100 candidatos, baseline + 10 elites + 10 imigrantes + 79 descendentes; melhor score 1,0 antes e depois, sem ganho demonstrado. Checkpoint e whitespace conferidos. Sem nova dependência, gasto, GPU ou alteração de interface. Nenhuma alegação de aprendizagem ou generalização.

## Par real preservado
Correção anterior: OST 24,5–50 s / piano 20–38 s, conforme região indicada pelo usuário. Ranking diagnóstico: 100 candidatos, 62 avaliações únicas, baseline/máximo 0,212052; training_allowed=false. Regiões indicadas não validam automaticamente cada nota do mapa interno DTW. Pacote privado P-IA-NO_Tifa_par_corrigido.zip preservado separadamente. Não repetir identificação da região nem substituir a referência por outro trecho sem evidência.

## Próximo bloco recomendado — 4.4 (aguardar autorização)
Múltiplas gerações com checkpoints e retomada determinística, inicialmente em referências controladas. Manter bloqueio dos diagnósticos reais. Currículo, alinhamento interno confiável, comparação auditiva, interface evolutiva e validação em músicas inéditas continuam pendentes.
