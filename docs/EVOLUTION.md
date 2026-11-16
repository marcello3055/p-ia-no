# Evolução — um ciclo controlado (4.3)

O motor usa os candidatos parametrizados existentes, não treina redes neurais. Entrada: população e ranking supervisionado correspondente, identificado por SHA-256 do manifesto e número da geração. Rankings diagnósticos/rejeitados ou com training_allowed=false são recusados.

Padrão: 100 configurações únicas; baseline preservado; até 10 elites, preferindo resultados musicais distintos; 10 imigrantes aleatórios; restante por recombinação uniforme dos três parâmetros e probabilidade 0,3 de mutar um gene. A melhor pontuação é preservada. A baseline pode também estar entre as elites. Parâmetros, semente, pais e origem de cada candidato ficam registrados. As entradas não são modificadas.

O espaço atual contém apenas 390 configurações de divisão entre mãos, quantidade de notas e alcance. Tentativas são limitadas a 20 vezes o tamanho da população, com preenchimento aleatório sem duplicatas. Configuração distinta não garante música distinta; diversidade musical é uma preferência na seleção das elites. Sementes tornam execuções reproduzíveis na mesma implementação. Populações menores exigem ajustar elites/imigrantes na API.

## Execução operada pelo agente
```sh
.venv/bin/python scripts/evolve_once.py fonte.mid referencia.mid --output-dir data/ciclo-1 --seed 0
```
A CLI executa somente gerações 0 e 1 e grava os dois manifestos, os dois rankings e resumo com hashes de entrada. Recusa destino existente. Não aceita rankings externos; calcula a comparação dos MIDIs fornecidos. Cabe ao operador fornecer trechos realmente correspondentes. Nenhum alinhamento é validado automaticamente por esta CLI.

## Evidência deste checkpoint
89 testes automatizados passaram, incluindo determinismo, preservação do melhor, mutação, diversidade de parâmetros, recusa de diagnósticos, entradas inválidas e término no espaço completo. Execução adicional em data/ranking-fixture: 100 candidatos; geração nova com baseline, 10 elites, 10 imigrantes e 79 descendentes. Melhor score antes/depois: 1,0/1,0. O exemplo controlado já atingia o máximo; não houve melhoria demonstrada.

O score compara notas, durações, harmonia temporal e ataques com uma referência. Não mede ainda expressividade, qualidade artística geral ou generalização. A referência de Tifa é áudio transcrito e seu mapa temporal interno continua experimental, portanto bloqueado para reprodução automática. Múltiplas gerações retomáveis, currículo cumulativo e interface ficam para blocos futuros. Sem novas dependências, GPU ou serviços pagos.

## Sessões retomáveis (4.4)
```sh
.venv/bin/python scripts/evolve_session.py fonte.mid referencia.mid --output-dir data/sessao --until 1
.venv/bin/python scripts/evolve_session.py fonte.mid referencia.mid --output-dir data/sessao --until 3 --resume
```
`--until` indica a geração final absoluta: 0 é a população inicial avaliada. Até 100 gerações novas por chamada, máximo absoluto 10000. Este bloco usa 100 candidatos e parâmetros evolutivos padrão. Fonte/referência devem ser MIDIs correspondentes fornecidos pelo operador; não há certificação automática de alinhamento. O par de Tifa permanece diagnóstico e não foi usado na sessão.

Cada generation-NNNNN.json contém população, ancestralidade, ranking e avaliações; SHA-256 encadeia os checkpoints e os vincula à configuração e às entradas. A semente de cada reprodução é (semente inicial + geração) módulo 2^32. A retomada valida todos os checkpoints, recusa lacunas, corrupção acidental, mudança de entrada/semente/código musical e não recalcula gerações completas. Checksums não são assinaturas contra adulteração deliberada. Reproduzir exige manter também ambiente/dependências fixados.

Gravação temporária + fsync + substituição atômica evita expor gerações incompletas. Interrupção durante uma geração preserva a última completa; apenas a geração incompleta será recalculada. Arquivos temporários de um processo morto são ignorados. Lock de processo (fcntl, Linux) impede dois escritores simultâneos; liberação ocorre ao encerrar processo. Não sobrescreve diretório existente sem --resume, nem aceita retroceder a geração. A sessão executa no terminal/backend, ainda sem fila web ou botão de pausa.

95 testes passaram. Execução CLI no exemplo controlado até geração 1 e retomada até 3: score máximo 1,0 em todas as gerações. Testes comparam arquivos de checkpoints da execução contínua e retomada byte a byte, simulam interrupção/falha de gravação, corrupção, lacunas, alteração de entradas, duplicidade de execução e limites. Não houve melhoria auditiva ou generalização demonstrada. Checkpoints em data/ são privados, fora do Git; precisam de backup próprio para sobreviver à perda do ambiente. GitHub preserva o código e o procedimento, não os dados de treinamento.
