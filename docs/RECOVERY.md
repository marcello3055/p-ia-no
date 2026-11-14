# Recuperação do checkpoint
O arquivo ZIP contém uma cópia dos arquivos e p-ia-no.bundle com histórico Git.
Estas instruções destinam-se ao agente; o usuário não precisa executar comandos.
1. Extrair o ZIP em diretório novo.
2. Executar `git clone p-ia-no.bundle p-ia-no-restored`.
3. Dentro do clone, verificar `git log -1` e `python scripts/check_checkpoint.py`.
4. Ler PROGRESS.md e obter autorização para o próximo bloco.
O remoto origin de um clone de bundle aponta para o arquivo local. Só mudar para GitHub após verificar o repositório privado correto e sua permissão. Se o remoto tiver README próprio, integrar histórias conscientemente; não fazer force-push.
Quando GitHub estiver disponível, ele passa a ser a fonte principal. Este pacote é o checkpoint anterior à sincronização remota, não substitui o compromisso com GitHub.
