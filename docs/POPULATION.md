# População inicial — Bloco 4.1
Primeira estrutura dos candidatos compartilhando o redutor existente. Não são redes neurais independentes. Sem avaliação, seleção, mutação, recombinação ou aprendizagem neste bloco.

## Parâmetros e reprodução
Padrão: 100 candidatos, semente 0, geração inicial identificada por 0. Tamanho configurável de 1 a 390: espaço inicial finito com 13 divisões entre mãos (48–72 em passos de 2), 5 capacidades simultâneas por mão (1–5) e 6 alcances (7–12 semitons). O tamanho máximo é limite deste espaço, não limite definitivo da plataforma. Restrições simplificadas não garantem tocabilidade.
Primeiro candidato sempre mantém o baseline (60,3,12). Restantes são amostrados sem reposição por gerador local com semente, sem alterar aleatoriedade global. ID deriva do hash dos parâmetros. Manifesto inclui versão, geração, semente e configurações completas; para recuperação durável, reutilizar manifesto em vez de depender apenas da semente/versão do Python. Manifestos inválidos, duplicados ou adulterados são recusados.

## Operação pelo agente
```sh
.venv/bin/python scripts/create_population.py entrada.mid --output-dir data/populacao-01 --size 100 --seed 0
.venv/bin/python scripts/create_population.py entrada.mid --output-dir data/replay-01 --population data/populacao-01/population.json
```
Entrada simbólica lida uma vez e reutilizada. Não transcreve áudio e não renderiza 100 MP3s. Pasta nova obrigatória; salva population.json, MIDIs gerados e results.json com hash da fonte, parâmetros no manifesto, contagens, descartes, hashes e falhas individuais. Resultado possui evaluated=0, best_candidate=null e score=null para não simular treinamento.
A saída musical é identificada por notas (mão, altura, início, fim e velocidade); diversidade de configurações não garante diversidade musical. O relatório conta saídas distintas nesse sentido, não qualidade/diversidade perceptual. Comparação de hashes vale dentro de mesma entrada/execução; não é métrica musical geral. Formas de acompanhamento, estratégias de vozes e expressividade ainda não variam neste espaço inicial.

## Verificado
76 testes aprovados (71 anteriores + 5): tamanho/seed, baseline, 390 configurações únicas, adulterações, geração de 100 MIDIs válidos, fonte imutável, músicas duplicadas, falha por ausência de notas, reprodução por manifesto e recusa de sobrescrita.
Execução adicional pelo CLI em exemplo sintético de 40 notas: 100 configurações, 100 MIDIs gerados, zero falhas, somente 4 saídas musicais distintas. Este exemplo evidencia a diferença entre diversidade paramétrica e musical. Nenhum ranking/melhoria alegado. Dados em data/population-4-1; podem ser regenerados e ficam fora do Git.

## Sequência
4.2: integrar avaliação explicável à população com referência simbólica controlada; registrar escores e ranking sem afirmar qualidade artística. Depois: seleção/reprodução/mutações, diversidade e checkpoints de múltiplas gerações. Interface, renderização dos melhores e feedback humano entram em blocos posteriores. Melhorias do transcritor serão retomadas conforme evidências; não bloqueiam a implementação do motor evolutivo simbólico.
