# Renderização inicial — Bloco 3.2
Renderizador offline Python/ctypes sobre libfluidsynth do sistema. Não abre dispositivo de áudio, não depende de GPU e não instala serviços. API oficial: https://www.fluidsynth.org/api/UsingSynth . FFmpeg com libmp3lame codifica o MP3.

## Dependências e licenças
Ambiente validado: FluidSynth 2.4.4, TimGM6mb.sf2 em /usr/share/sounds/sf2/TimGM6mb.sf2 e FFmpeg existente. O banco e a biblioteca já estavam disponíveis; o gerenciador dpkg não expõe seus registros neste ambiente. Sem instalação ou cobrança.
- FluidSynth: LGPL-2.1-or-later conforme /usr/share/doc/libfluidsynth3/copyright e https://www.fluidsynth.org/wiki/LicensingFAQ/ .
- TimGM6mb: Tim Brechbill (2004), David Bolton (2010), GPL-2 conforme /usr/share/doc/timgm6mb-soundfont/copyright. Origem: https://sources.debian.org/src/timgm6mb-soundfont/ . Banco GM pequeno; somente banco 0/programa 0 utilizado. Qualidade inicial, não piano final aprovado.
- FFmpeg: software livre; licença efetiva depende da compilação. Ver `ffmpeg -L` no ambiente de execução. Não redistribuímos binários ou SoundFont no Git. Instalações futuras devem preservar avisos e cumprir licenças dos pacotes.

Em Debian/Ubuntu, dependências de sistema esperadas: libfluidsynth3, timgm6mb-soundfont, ffmpeg. A instalação fica a cargo do agente no ambiente de implantação, não do usuário. Não há novas dependências pip. Ausência de biblioteca, amostras ou codificador gera erro explícito.

## Contrato
`scripts/render_piano.py entrada.mid --output-dir pasta-nova` (executar com .venv/bin/python). Entrada deve ser MIDI reduzido: canal 0, programa 0, sem controladores, notas positivas no piano e sem mesma tecla sobreposta entre trilhas. Limite experimental de 120 segundos, não duração final do produto. Destino deve ser novo. Saídas: piano.wav, piano.mp3 e render.json. Não é endpoint web; usar apenas MIDI/SoundFont confiáveis no protótipo interno.
WAV estéreo PCM16/44,1 kHz; MP3 192 kbit/s. Ganho 0,2, chorus/reverb desativados, cauda fixa de 3 segundos. Usa tempos e velocidades das notas; note-offs antes dos reataques. Sem pedal, rubato novo ou interpretação humanizada. A cauda fixa pode truncar ressonâncias longas. Não preserva velocidade de soltura. Rejeita áudio silencioso ou PCM saturado; não há normalização automática.

Relatório registra versões reais, parâmetros, pico PCM, contagem/duração e SHA-256 do MIDI, SoundFont e saídas. Não garante identidade binária entre plataformas/versões. Pasta parcial removida em falha normal; interrupção abrupta ainda pode deixar arquivos. Áudio/modelos ficam fora do Git e exigem armazenamento próprio em implantação.

## Verificação
Teste real percorre redução → MIDI → WAV → MP3 → decodificação FFmpeg. Verifica duração, estéreo, taxa, sinal e pico; testa também destino existente, SoundFont ausente, duração excessiva e programa não pianístico. Não equivale a escuta humana. Nenhuma música privada usada. Transcrição de MP3 orquestral e player para resultados gerados continuam pendentes.
