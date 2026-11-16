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
