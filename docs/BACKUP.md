# Backup e restauração — Bloco 1.3

## Para o usuário
Na aplicação, Meus modelos → Baixar backup dos dados. Aguarde o download terminar e guarde o ZIP no seu dispositivo, fora do servidor de desenvolvimento. Não há envio automático para provedores externos. Isso não exige contratar serviço pago. Ainda não existe endereço público permanente da aplicação.
Para recuperar, disponibilize o ZIP ao agente e peça restauração. O agente fará as operações técnicas. Não há importação pelo navegador neste bloco.

## Conteúdo e limites
Formato ZIP com manifest.json (schema_version 1) e audio/<UUID>.<extensão>. Inclui todos os áudios registrados, nomes e relações dos pares, IDs e datas; não inclui modelo de IA, código, credenciais, arquivos órfãos ou SQLite executável. SHA-256 detecta alteração em relação ao manifesto; não é assinatura de autenticidade. Aceitar apenas backups de origem conhecida. Arquivo não criptografado: contém músicas e nomes originais.
Mesmos limites do armazenamento: 100 MiB por áudio, 1 GiB total, 30 minutos por áudio; até 9.999 áudios, 10.000 pares e manifesto de 8 MiB. Sem restauração em pasta existente, mesclagem ou sobrescrita. Versões desconhecidas são recusadas.

## Procedimento para o agente
Usar o repositório vigente, Python isolado e ffprobe já disponíveis. Para CLI, parar o servidor antes de exportar ou restaurar. Não executar vários workers. Confirmar diretório de origem e escolher destino novo; nunca apontar para banco existente.

Exportar: `.venv/bin/python scripts/backup.py export --data-dir /caminho/dados --output /caminho/novo-backup.zip`
Restaurar: `.venv/bin/python scripts/backup.py restore --archive /caminho/backup.zip --destination /caminho/dados-recuperados`

Após restauração bem-sucedida, iniciar uma instância local com PIANO_DATA_DIR apontando ao destino e verificar /api/audio, /api/pairs e reprodução. Preservar a origem antiga até validar. Não mudar automaticamente a biblioteca ativa só porque o ZIP foi validado.

O endpoint GET /api/backup cria um snapshot dos registros em transação SQLite; usa lock do processo para não competir com upload. Arquivos registrados são imutáveis. Cria ZIP temporário e o remove após resposta; o download nativo evita carregar o ZIP inteiro no JavaScript da página. Em falha retorna 409, não um ZIP incompleto. CLI exige origem existente e publicação do ZIP sem sobrescrita.

## Validação da restauração
Lista exata de entradas permitidas, limites, rejeição de duplicatas/links/criptografia/caminhos fora do padrão, validação de schema e relações, cópia incremental com tamanho e SHA-256, verificação de formato/duração com ffprobe, banco novo com parâmetros SQL. Nunca executar SQL, pickle ou programas vindos do arquivo. Em falha, remover somente a pasta criada pela própria restauração.

## Durabilidade
Backup no mesmo ambiente continua sujeito a perda. A primeira opção sem contratação é baixar e guardar o ZIP no dispositivo do usuário. Armazenamento externo automático e hospedagem ficam pendentes de escolha/acesso, sem promessa de serviço gratuito permanente. Não usar GitHub para músicas. Queda abrupta durante backup/restore pode deixar temporários; recuperação disso permanece pendente. API não autenticada é somente para desenvolvimento, nunca publicação aberta.
