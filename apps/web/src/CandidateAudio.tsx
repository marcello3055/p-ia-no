import { useEffect, useRef, useState } from 'react';
export function CandidateAudio({sessionId,generation,candidateId}:{sessionId:string;generation:number;candidateId:string}) {
  const [url,setUrl]=useState('');
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  const request=useRef<AbortController|null>(null);
  const resource=useRef('');
  useEffect(()=>()=>{request.current?.abort();if(resource.current)URL.revokeObjectURL(resource.current);},[]);
  async function prepare(){
    const controller=new AbortController(); request.current=controller;
    setBusy(true);setError('');
    const timer=setTimeout(()=>{controller.abort();setBusy(false);setError('O áudio demorou a ficar pronto. Tente novamente em instantes.');},180000);
    try {
      const response=await fetch(`/api/sessions/${encodeURIComponent(sessionId)}/generations/${generation}/candidates/${candidateId}/audio`,{method:'POST',signal:controller.signal});
      if(!response.ok){const body=await response.json();throw new Error(body.detail||'Não foi possível preparar o áudio.');}
      const blob=await response.blob();
      if(!controller.signal.aborted){resource.current=URL.createObjectURL(blob);setUrl(resource.current);}
    } catch(e){if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Falha ao preparar áudio.');}
    finally{clearTimeout(timer);if(!controller.signal.aborted)setBusy(false);}
  }
  return <div className="candidate-audio">
    {!url&&<button className="secondary" disabled={busy} onClick={()=>void prepare()}>{busy?'Preparando piano…':'Preparar áudio de piano'}</button>}
    {busy&&<p role="status">Renderizando a proposta selecionada. Isso não inicia novo treinamento.</p>}
    {error&&<p role="alert" className="error">{error}</p>}
    {url&&<><audio controls preload="metadata" src={url} aria-label={`Piano do candidato ${candidateId}`} onError={()=>setError('Não foi possível reproduzir o áudio neste navegador.')} onPlay={event=>{document.querySelectorAll('audio').forEach(other=>{if(other!==event.currentTarget)other.pause();});}}/><a className="backup-link" href={url} download={`geracao-${generation}-${candidateId}.mp3`}>Baixar MP3 deste candidato</a></>}
    <p className="hint">Piano virtual inicial, sem nova expressividade ou pedal. Trechos de até 120 segundos. O áudio fica temporariamente disponível nesta consulta.</p>
  </div>;
}
