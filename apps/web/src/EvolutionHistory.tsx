import { useEffect, useState } from 'react';
type Row = { generation:number; best_score:number|null; baseline_score:number|null; evaluated:number; failed:number; unique_evaluations:number; diagnostic:boolean };
type Session = { id:string; state:string; population_size:number; generation:number|null; history:Row[] };
const score = (value:number|null) => value === null ? '—' : value.toFixed(3).replace('.', ',');
export function EvolutionHistory() {
  const [ids,setIds] = useState<string[]>([]);
  const [selected,setSelected] = useState('');
  const [session,setSession] = useState<Session|null>(null);
  const [error,setError] = useState('');
  const [loading,setLoading] = useState(false);
  const [revision,setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true); setError(''); setSession(null);
    const timer=setTimeout(()=>{controller.abort();setLoading(false);setError('O servidor demorou a responder. Tente atualizar o histórico.');},10000);
    async function load() {
      try {
        const response=await fetch('/api/sessions',{signal:controller.signal,cache:'no-store'});
        if(!response.ok) throw new Error('Não foi possível consultar as sessões.');
        const data=await response.json();
        const names:string[]=data.sessions.map((item:{id:string})=>item.id);
        setIds(names);
        const id=names.includes(selected)?selected:(names[0]||'');
        if(id!==selected) { setSelected(id); return; }
        if(id) {
          const result=await fetch(`/api/sessions/${encodeURIComponent(id)}`,{signal:controller.signal,cache:'no-store'});
          if(!result.ok) throw new Error(result.status===409?'Histórico indisponível: integridade ou limite de consulta.':'Não foi possível carregar o histórico.');
          setSession(await result.json());
        }
      } catch(e) {
        if(!controller.signal.aborted) setError(e instanceof Error?e.message:'Falha de conexão.');
      } finally { if(!controller.signal.aborted) setLoading(false); clearTimeout(timer); }
    }
    void load();
    return ()=>{clearTimeout(timer);controller.abort();};
  },[selected,revision]);
  return <section className="midi-compare" aria-labelledby="evolution-title">
    <p className="eyebrow">LABORATÓRIO EXPERIMENTAL</p><h2 id="evolution-title">Histórico das gerações</h2>
    <p>Consulte as sessões executadas pelo agente. As pontuações comparam os candidatos com uma referência simbólica; não representam uma nota de qualidade musical.</p>
    <div className="save-actions"><label htmlFor="evolution-session">Sessão<select id="evolution-session" value={selected} onChange={e=>setSelected(e.target.value)} disabled={loading||ids.length===0}>{ids.length===0&&<option value="">Nenhuma sessão</option>}{ids.map(id=><option key={id}>{id}</option>)}</select></label>
      <button className="secondary" onClick={()=>setRevision(n=>n+1)}>Atualizar histórico</button></div>
    <p role="status">{loading?'Carregando histórico…':error?'':ids.length===0?'Nenhuma sessão evolutiva salva neste ambiente.':''}</p>
    {error&&<p className="error" role="alert">{error}</p>}
    {session&&<><p><strong>{session.population_size} candidatos por geração</strong> · {session.state==='busy'?'Sessão em uso por outro processo':'Sem processo ativo'} · Última geração salva: {session.generation??'nenhuma'}</p>
      <p className="hint">Sem processo ativo não significa treinamento concluído. Use Atualizar histórico para consultar novos checkpoints. Geração 0 é a população inicial.</p>
      <div className="metric-table" tabIndex={0} role="region" aria-label="Pontuações por geração"><table><caption>Pontuações de 0 a 1 — valores calculados e salvos</caption><thead><tr><th scope="col">Geração</th><th scope="col">Melhor</th><th scope="col">Baseline</th><th scope="col">Avaliados</th><th scope="col">Falhas</th><th scope="col">Resultados únicos avaliados</th><th scope="col">Uso</th></tr></thead><tbody>{session.history.map(row=><tr key={row.generation}><td>{row.generation}</td><td>{score(row.best_score)}</td><td>{score(row.baseline_score)}</td><td>{row.evaluated}</td><td>{row.failed}</td><td>{row.unique_evaluations}</td><td>{row.diagnostic?'Somente diagnóstico':'Referência simbólica'}</td></tr>)}</tbody></table></div>
      {session.history.length===0&&<p>Nenhuma geração completa salva.</p>}</>}
    <p className="hint">Neste bloco, a consulta é somente leitura. Iniciar sessões, ouvir candidatos e aprovar arranjadores pelo painel serão etapas posteriores.</p>
  </section>;
}
