import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';
type Status = 'checking' | 'online' | 'offline';
function App() {
  const [status, setStatus] = useState<Status>('checking');
  const [retry, setRetry] = useState(0);
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
    <section className="connection" aria-labelledby="connection-title"><div><p className="eyebrow">BASE DO PROJETO · BLOCO 0.2</p><h2 id="connection-title">Conexão com o serviço</h2><p role="status" aria-live="polite">{status === 'checking' ? 'Verificando conexão…' : status === 'online' ? 'API conectada. A base está funcionando.' : 'Não foi possível conectar. Tente novamente.'}</p></div><button disabled={status === 'checking'} onClick={() => setRetry(n => n + 1)}>Verificar novamente</button></section>
    <section className="roadmap" aria-label="Ambientes planejados">{[['01', 'Treinamento', 'Exemplos musicais, evolução e avaliação dos arranjadores.'], ['02', 'Arranjar', 'Novas músicas, interpretadas pelo arranjador que você aprovou.'], ['03', 'Meus modelos', 'Versões preservadas para voltar, comparar e reutilizar.']].map(([n,title,desc]) => <article key={n}><span className="number">{n}</span><h2>{title}</h2><p>{desc}</p><span className="planned">Planejado · ainda indisponível</span></article>)}</section>
    <footer>Este checkpoint verifica somente a interface e a API. Uploads, treinamento e geração de áudio ainda não estão disponíveis.</footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
