import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';
import { AudioInput } from './AudioInput';
import { MidiCompare } from './MidiCompare';
import { SavedLibrary } from './SavedLibrary';
type Status = 'checking' | 'online' | 'offline';
function App() {
  const [status, setStatus] = useState<Status>('checking');
  const [retry, setRetry] = useState(0);
  const [tab, setTab] = useState(0);
  const [base, setBase] = useState<File | null>(null);
  const [reference, setReference] = useState<File | null>(null);
  const [studio, setStudio] = useState<File | null>(null);
  const tabs = ['Treinamento', 'Arranjar', 'Meus modelos'];
  function selectTab(index: number) {
    document.querySelectorAll('audio').forEach(audio => audio.pause());
    setTab(index);
  }
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setStatus('checking');
    const timer = setTimeout(() => controller.abort(), 5000);
    fetch('/api/health', { signal: controller.signal, cache: 'no-store' })
      .then(async response => {
        if (!response.ok) throw new Error('API unavailable');
        const data = await response.json();
        if (data.status !== 'ok' || data.service !== 'p-ia-no-api') throw new Error('Unexpected response');
        if (active) setStatus('online');
      }).catch(() => { if (active) setStatus('offline'); })
      .finally(() => clearTimeout(timer));
    return () => { active = false; clearTimeout(timer); controller.abort(); };
  }, [retry]);
  return <main>
    <header><a href="/" aria-label="P-IA-NO, início">P-IA-NO<span>ORQUESTRA → PIANO</span></a><span className="badge">Em desenvolvimento</span></header>
    <section className="hero"><p className="eyebrow">UMA NOVA FORMA DE OUVIR</p><h1>A essência da orquestra.<br/><em>A expressão do piano.</em></h1><p className="intro">Seu espaço para desenvolver, aperfeiçoar e preservar arranjadores de piano solo.</p></section>
    <aside className="notice">Selecionar um arquivo permite ouvi-lo localmente. Para guardá-lo neste ambiente, use Salvar. Os arquivos salvos sobrevivem ao reinício da aplicação, mas podem se perder se o ambiente de desenvolvimento for descartado.</aside>
    <div className="tabs" role="tablist" aria-label="Ambientes do P-IA-NO">{tabs.map((label, i) => <button key={label} id={`tab-${i}`} role="tab" aria-selected={tab === i} aria-controls={`panel-${i}`} tabIndex={tab === i ? 0 : -1} onClick={() => selectTab(i)} onKeyDown={event => {
      let next = i;
      if (event.key === 'ArrowRight') next = (i + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (i + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault(); selectTab(next); document.getElementById(`tab-${next}`)?.focus();
    }}>{label}</button>)}</div>
    <section id="panel-0" role="tabpanel" aria-labelledby="tab-0" hidden={tab !== 0} tabIndex={0}><h2>Ouça seus exemplos</h2><p>Selecione a gravação orquestral e o arranjo correspondente para piano. Por enquanto, você pode ouvir e comparar os arquivos originais.</p><div className="audio-grid"><AudioInput id="orchestra" title="Música-base · orquestra" onFileChange={setBase}/><AudioInput id="reference" title="Música-objetivo · piano" onFileChange={setReference}/></div><SavedLibrary mode="pairs" first={base} second={reference}/><p className="hint">Salvar exemplos ainda não inicia treinamento.</p><MidiCompare/></section>
    <section id="panel-1" role="tabpanel" aria-labelledby="tab-1" hidden={tab !== 1} tabIndex={0}><h2>Prepare uma nova música</h2><p>Ouça a gravação que você deseja transformar em piano solo.</p><AudioInput id="studio" title="Música inédita" onFileChange={setStudio}/><SavedLibrary mode="audio" first={studio}/><div className="empty"><h3>A geração de arranjos ainda não está disponível</h3><p>Este player reproduz somente o áudio original. A seleção de arranjadores e a geração de piano serão adicionadas em etapas futuras.</p></div></section>
    <section id="panel-2" role="tabpanel" aria-labelledby="tab-2" hidden={tab !== 2} tabIndex={0}><div className="empty"><p className="eyebrow">SUA BIBLIOTECA</p><h2>Nenhum arranjador disponível</h2><p>Quando o treinamento e a aprovação forem implementados, suas versões aprovadas aparecerão aqui. Ainda não foram criados ou treinados modelos.</p></div><section className="empty" aria-label="Backup dos dados"><h2>Proteja seus áudios e exemplos</h2><p>Baixe uma cópia dos áudios salvos e dos pares de treinamento. O arquivo não inclui arranjadores de IA, pois ainda não existem modelos treinados.</p><a className="backup-link" href="/api/backup" download="P-IA-NO-dados.zip">Baixar backup dos dados</a><p className="hint">Guarde o ZIP fora deste ambiente. O backup não é automático nem criptografado. Para recuperar os dados, envie o arquivo ao agente: a restauração será feita em uma pasta nova, sem apagar a biblioteca atual.</p></section></section>
    <section className="connection" aria-labelledby="connection-title"><div><p className="eyebrow">STATUS DO SERVIÇO</p><h2 id="connection-title">Conexão com o servidor</h2><p role="status" aria-live="polite">{status === 'checking' ? 'Verificando conexão…' : status === 'online' ? 'Servidor conectado.' : 'Servidor indisponível. A reprodução local continua disponível.'}</p></div><button disabled={status === 'checking'} onClick={() => setRetry(n => n + 1)}>Verificar novamente</button></section>
    <footer>Bloco 2.3 · comparação MIDI e backup manual. Sem hospedagem permanente, treinamento ou geração de piano.</footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
