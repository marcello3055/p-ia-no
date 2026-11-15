# Preparação de áudio — MP3-2a
Bloco preparatório para o ensaio com gravação real, sem transcrição nova ou integração web. Opera sobre arquivo local fornecido/autorizado; não baixa URLs. O usuário pode enviar a música inteira, sem conversão ou corte manual.

## Operação pelo agente
```sh
.venv/bin/python scripts/prepare_audio_clip.py entrada.mp3 --output-dir data/trecho-01 --start 30 --seconds 20
```
Reutiliza FFmpeg/FFprobe já presentes, sem dependências novas. Limites: arquivo 100 MiB, duração 30 minutos, trecho 1–30 segundos; padrão 20 segundos desde o início. Detecta formato real MP3/WAV/FLAC, ignora extensão enganosa, valida números finitos. Decodifica primeiro fluxo de áudio; aceita arquivo local, restringe protocolos a file/pipe. Não expor como endpoint público: ainda não há isolamento de decodificador para arquivos adversariais.
Saída clip.wav mono PCM16 a 22.050 Hz, compatível com a entrada do experimento Basic Pitch; clip.json registra hash do original, posição, duração solicitada/efetiva, formato, versão FFmpeg, parâmetros, hash do WAV e pico PCM. Sinaliza silêncio exato e truncamento no fim. Não normaliza, não identifica frases, não seleciona automaticamente o melhor trecho e não calibra confiança. Downmix pode cancelar canais fora de fase.

## Cache e preservação
Mesma entrada (SHA-256), posição/duração, versão e parâmetros reutilizam saída cujo hash confere. Configuração diferente ou cache corrompido exige pasta nova; nunca sobrescreve dados existentes. Original permanece intacto. Consulta de metadados/hash ainda ocorre na reutilização, mas a decodificação não se repete. Falhas normais limpam temporários; interrupção abrupta pode deixar saída parcial, que será recusada como cache. Arquivos e relatórios privados ficam em data/, fora do Git; não são incluídos automaticamente na biblioteca/backup do site.

## Testes
Cinco testes novos: recorte MP3 real, taxa/canais/amostras, original intacto e cache sem regravação; fim/silêncio; limites/conteúdo inválido; configuração alterada/cache corrompido; WAV/FLAC e CLI. 71 testes totais aprovados. Fontes dos testes são tons sintéticos, sem evidência de qualidade de transcrição orquestral. Próximo passo depende de gravação real autorizada.
