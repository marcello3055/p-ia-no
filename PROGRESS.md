# Progresso — Bloco 3.1
Data: 15/11/2026. Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior remoto: a7009dab9b486c59971db2d0af7a860c035c8fc0 (2.4).
O commit deste documento constitui o checkpoint 3.1.

## Implementado
Redutor simbólico determinístico com prioridade grave/aguda, mãos separadas, alcance e polifonia configuráveis, tratamento de sustentação e duplicatas. MIDI de piano com tempo preservado; relatório de seleção/descarte e parâmetros. CLI sem sobrescrever arquivos, hashes de entrada/saída. Nenhuma dependência nova, GPU ou serviço pago.

## Testado
60 testes aprovados (53 anteriores + 7 novos). Novos casos: redução de acordes, limites durante sustentação, duplicatas/reataques, exclusão de percussão e notas fora do piano, remoção de instrumentos/controladores, tempo, imutabilidade, determinismo, entradas inválidas, exportação/releitura e CLI sem sobrescrita. Sem alterações no frontend; build/navegador não repetidos. Aviso de depreciação Starlette/httpx permanece sem falha.

## Limitações
Algoritmo experimental, não modelo treinado. Voz aguda não é reconhecimento de melodia; limites de mão não garantem tocabilidade. Sem qualidade artística/auditiva validada, acompanhamento novo, pedal ou expressividade. Uso interno pelo agente, sem API/UI para redução. Não gera áudio nem transcreve MP3. Upload/reprodução de MP3 dos blocos anteriores permanecem disponíveis no ambiente de desenvolvimento. Objetivo final continua upload MP3 orquestral e saída piano audível, sem conversão manual pelo usuário.
Hospedagem permanente, autenticação, validação Android, backup externo automático e músicas reais seguem pendentes. Dados musicais privados fora do Git.

## Próximo bloco recomendado — 3.2 (aguardar autorização)
Renderização inicial do MIDI em áudio de piano com ferramenta e amostras gratuitas de licença compatível. Verificar disponibilidade/licenças antes de instalar; testar saída audível WAV e, se viável, MP3. Não iniciar transcrição nem treinamento evolutivo nesse bloco.
