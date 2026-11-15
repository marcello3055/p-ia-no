# Progresso — prova MP3-1
Data: 15/11/2026. Repositório: https://github.com/marcello3055/p-ia-no
Checkpoint anterior: f90e1a960c6c50b1331e53d69f465ae0f900da0a (planejamento URL); último funcional web: ff2bb71064ad44deb7247929241b61a5121deb4b.
O commit deste documento é o checkpoint do experimento MP3-1.

## Executado
Basic Pitch 0.4.0 com modelo ONNX oficial do pacote PyPI, inferência real em CPU. Ambiente .venv-audio isolado: TensorFlow declarado upstream não é compatível com Python 3.12; alternativa ONNX instalada explicitamente, setuptools 80.9.0 resolve pkg_resources do resampy. Dependências fixadas, script de reprodução, modelo/SoundFont identificados por hash. Nenhum gasto, GPU, download de música alheia, treinamento ou mudança na aplicação.
Criados três MP3s sintéticos com FluidSynth/TimGM6mb e notas conhecidas: melodia de piano, acordes e flauta+cordas. Script preserva ativações e eventos; relatório textual incluído no Git, áudios/pesos fora do Git.

## Resultados reais
Melodia: 8 notas esperadas, 12 estimadas, 8 correspondências; F1 altura/ataque 0,800.
Acordes: 16 esperadas, 19 estimadas, 16 correspondências; F1 0,914.
Mistura: 24 esperadas, 46 estimadas, 23 correspondências; precisão 0,500, F1 0,657.
F1 incluindo duração: 0,000 / 0,571 / 0,171 respectivamente. Critérios: altura exata, ataque ±100 ms, duração ±máximo(150 ms,20%). Não são avaliações de qualidade artística. Pico RSS 423,64 MiB; inferência inicial 11,54 s e posteriores ~0,10–0,11 s em trechos de cerca de 7 s. Primeiro caso inclui preparação/JIT; não extrapolar tempos.

## Verificação
Três inferências completas; conferidos arquivos MP3 e consistência dos relatórios. Python compila, script shell validado, verificação do checkpoint e git diff --check. Sem repetir os 66 testes da aplicação pois nenhum código/dependência dela foi alterado. Receita de reinstalação registrada, não repetida em ambiente limpo. Não houve escuta artística.

## Limites e decisão
Viabilidade computacional demonstrada; fidelidade orquestral NÃO demonstrada. Basic Pitch é documentado upstream como melhor para um instrumento por vez. Mistura sintética evidenciou muitas notas extras e erros de duração. Ativações não são confiança calibrada. Sem reconhecimento de melodia, separação, alinhamento ou expressividade. Não integrado ao site. Dados binários locais podem expirar, mas receita e resultados controlados estão versionados.
Planejamento de URLs permanece preservado em docs/URL_IMPORT.md; nenhuma extração implementada.

## Próximo bloco recomendado — MP3-2 (aguardar autorização e arquivo)
Testar um trecho orquestral real autorizado, de preferência 15–30 segundos, fornecido pelo usuário ou outra fonte autorizada verificada. Inspecionar notas extras e durações; comparar áudio/transcrição sem alegar precisão objetiva quando não houver referência simbólica. Não iniciar treinamento evolutivo nem concluir que Basic Pitch será o transcritor definitivo. Não converter manualmente o arquivo pelo usuário.
