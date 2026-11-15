import { useEffect, useRef, useState } from 'react';
type Download = {name: string; url: string};
export function PianoExperiment() {
  const [file,setFile]=useState<File|null>(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  const [downloads,setDownloads]=useState<Download[]>([]);
  const [summary,setSummary]=useState('');
  const urls=useRef<string[]>([]);
  const controller=useRef<AbortController|null>(null);
  function clear() {
    urls.current.forEach(URL.revokeObjectURL); urls.current=[];
    setDownloads([]); setSummary(''); setError('');
  }
  useEffect(()=>()=>{controller.current?.abort(); urls.current.forEach(URL.revokeObjectURL);},[]);
  async function generate() {
    if (!file || busy) return;
    clear(); setBusy(true);
    const abort=new AbortController(); controller.current=abort;
    const timer=setTimeout(()=>abort.abort(),180000);
    try {
      const response=await fetch('/api/experimental/piano',{method:'POST',headers:{'Content-Type':'application/octet-stream'},body:file,signal:abort.signal});
      const data=await response.json();
      if (!response.ok) throw new Error(typeof data.detail==='string'?data.detail:'Não foi possível gerar o piano.');
      const result:Download[]=data.files.map((item:{name:string; mime:string; base64:string})=>{
        const raw=atob(item.base64); const bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));
        const url=URL.createObjectURL(new Blob([bytes],{type:item.mime})); urls.current.push(url);
        return {name:item.name,url};
      });
      const report=URL.createObjectURL(new Blob([JSON.stringify(data.report,null,2)],{type:'application/json'}));
      urls.current.push(report); result.push({name:'relatorio-piano.json',url:report});
      setDownloads(result);
      setSummary(`${data.report.selection.input_notes} notas de entrada → ${data.report.selection.output_notes} notas de piano. Áudio: ${data.report.rendering.duration_seconds.toFixed(1)} segundos, incluindo a cauda sonora.`);
    } catch (e) {
      clear(); setError(e instanceof Error && e.name==='AbortError'?'Tempo de espera esgotado. O servidor pode ainda estar concluindo a tarefa.':e instanceof Error?e.message:'Falha na geração.');
    } finally {clearTimeout(timer); controller.current=null; setBusy(false);}
  }
  return <section className="empty" aria-labelledby="experiment-title">
    <p className="eyebrow">FERRAMENTA EXPERIMENTAL · ENTRADA MIDI</p>
    <h2 id="experiment-title">Ouça a primeira redução para piano</h2>
    <p>Teste interno do motor: seleciona notas e distribui entre duas mãos, depois gera áudio de piano. Ainda não analisa MP3 orquestral nem usa arranjadores treinados.</p>
    <label htmlFor="piano-midi">MIDI de teste · até 5 MiB e 120 segundos</label>
    <input id="piano-midi" type="file" accept=".mid,.midi" disabled={busy} onChange={event=>{
      clear(); setFile(null); const selected=event.target.files?.[0];
      if (!selected) return;
      if (!/\.(mid|midi)$/i.test(selected.name)||!selected.size||selected.size>5*1024**2) {
        setError('Escolha um MIDI não vazio de até 5 MiB. O upload de MP3 está no painel acima.'); event.target.value=''; return;
      }
      setFile(selected);
    }}/>
    <p><button disabled={!file||busy} onClick={generate}>{busy?'Gerando piano…':'Gerar piano experimental'}</button></p>
    <p role="status" aria-live="polite">{busy?'Enviando, reduzindo e renderizando no servidor. Aguarde; não há progresso percentual disponível.':summary}</p>
    {error&&<p role="alert" className="notice">{error}</p>}
    {downloads.length>0&&<div><h3>Resultado gerado · piano solo</h3><audio aria-label="Piano gerado" controls preload="metadata" src={downloads.find(d=>d.name==='piano.mp3')?.url}/><p>{downloads.map(d=><a className="backup-link" key={d.name} href={d.url} download={d.name}>Baixar {d.name} </a>)}</p></div>}
    <p className="hint">Resultado temporário: baixe os arquivos antes de trocar a entrada ou fechar a página. Não entra no histórico nem no backup. Qualidade musical e tocabilidade ainda não validadas; sem pedal ou expressividade nova. Você não precisará converter MP3 manualmente no produto final.</p>
  </section>;
}
