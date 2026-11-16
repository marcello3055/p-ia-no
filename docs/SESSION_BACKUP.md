# Backup de sessões evolutivas — 4.5

Operação pelo agente, sem ação técnica do usuário. O pacote privado contém source.mid, reference.mid, session.json, gerações completas e manifesto com tamanho/hash de cada arquivo, versão Python e mido. Não inclui áudio original, credenciais, modelos, código executável ou dependências. As entradas MIDI são a representação efetivamente usada nesta sessão; áudio original e transcrição precisam de preservação separada. Não equivale à exportação futura de arranjador aprovado.

```sh
.venv/bin/python scripts/session_backup.py export --session data/sessao --source fonte.mid --reference referencia.mid --output data/sessao.zip
.venv/bin/python scripts/session_backup.py restore --archive data/sessao.zip --destination data/recuperada
.venv/bin/python scripts/evolve_session.py data/recuperada/source.mid data/recuperada/reference.mid --output-dir data/recuperada --until 4 --resume
```
Na retomada, fornecer a mesma semente original com --seed se diferente de zero. A geração final deve ser igual ou posterior à última salva. Restauração requer o código musical original e mesmas versões Python/mido; recupere o checkpoint Git correspondente e dependências fixadas. O pacote não instala nem executa código. A verificação de código existente permanece inalterada, preservando compatibilidade com sessões do bloco 4.4.

Exportação adquire lock e copia somente gerações completas, valida o retrato e publica ZIP sem sobrescrever destino. Restauração usa pasta temporária, verifica inventário, SHA-256, encadeamento dos checkpoints, entradas e ambiente antes de publicar a pasta completa. Recusa destinos existentes, caminhos fora da lista permitida, duplicatas, links, diretórios, conteúdo cifrado, arquivos acima de 16 MiB e conteúdo total/ZIP acima de 64 MiB. MIDI mantém limite próprio de 5 MiB. Limite de 10004 arquivos de dados. SHA-256 detecta corrupção; não autentica a autoria de pacotes deliberadamente adulterados. Operação requer Linux/sistema de arquivos local compatível.

## Evidência
102 testes passaram, incluindo exportação/restauração com checkpoints idênticos, continuação determinística, corrupção de arquivos e cadeia, caminhos indevidos, duplicatas, links, limites, ambiente incompatível e proteção contra sobrescrita. Sessão controlada anterior exportada na geração 3, restaurada em nova pasta e continuada até 4. Melhor score permaneceu 1,0, sem demonstração de ganho musical.

O ZIP de ensaio fica em data/session-4-5.zip e a recuperação em data/session-restored-4-5, ambos fora do Git. Este bloco implementa portabilidade, não armazenamento externo automático; para sobreviver à perda do ambiente, o pacote deve ser copiado a armazenamento durável ou baixado. Exemplo sintético é reproduzível a partir dos testes. O par real Tifa não foi modificado nem utilizado.
