import { useEffect, useState } from 'react';
type Values = Record<string,number|null>;
type Candidate = {id:string; rank:number; score:number; output_notes:number; criteria:Values; contributions:Values; config:{split_pitch:number;max_notes_per_hand:number;max_span:number}};
type Details = {generation:number;weights:Values;diagnostic:boolean;total_evaluated:number;total_failed:number;best_tie_count:number;candidates:Candidate[]};
const criteria = [['pitch_onset','Alturas e início das notas'],['duration','Notas com duração correspondente'],['pitch_classes','Classes de altura ao longo do tempo'],['attacks','Padrão rítmico de ataques']];
const number = (value:number|null) => value===null?'Não disponível':value.toFixed(3).replace('.',',');
export function GenerationCandidates({sessionId,generations}:{sessionId:string;generations:number[]}) {
  const [generation,setGeneration]=useState(generations[generations.length-1]);
  const [details,setDetails]=useState<Details|null>(null);
  const [error,setError]=useState('');
  const [loading,setLoading]=useState(false);
  const [retry,setRetry]=useState(0);
  useEffect(()=>{
    const controller=new AbortController();
    setDetails(null);setError('');setLoading(true);
    const timer=setTimeout(()=>{controller.abort();setLoading(false);setError('A consulta demorou a responder. Tente novamente.');},10000);
    async function load(){
      try {
        const response=await fetch(`/api/sessions/${encodeURIComponent(sessionId)}/generations/${generation}`,{signal:controller.signal,cache:'no-store'});
        if(!response.ok) throw new Error(response.status===404?'Geração não encontrada.':'Não foi possível verificar os candidatos salvos.');
        const data=await response.json();
        if(!controller.signal.aborted)setDetails(data);
      } catch(e){if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Falha na consulta.');}
      finally{clearTimeout(timer);if(!controller.signal.aborted)setLoading(false);}
    }
    void load();return()=>{clearTimeout(timer);controller.abort();};
  },[sessionId,generation,retry]);
  return <section aria-labelledby="candidates-heading">
    <h3 id="candidates-heading">Melhores candidatos da geração</h3>
    <label htmlFor="candidate-generation">Escolha a geração</label>
    <select id="candidate-generation" value={generation} onChange={e=>setGeneration(Number(e.target.value))}>{generations.map(g=><option key={g} value={g}>Geração {g}</option>)}</select>
    {loading&&<p role="status">Consultando avaliações salvas…</p>}
    {error&&<><p role="alert" className="error">{error}</p><button className="secondary" onClick={()=>setRetry(n=>n+1)}>Tentar novamente</button></>}
    {details&&<><p>{details.total_evaluated} avaliados · {details.total_failed} falhas · {details.best_tie_count} empatados na melhor pontuação.</p>
      {details.diagnostic&&<p className="notice">Somente diagnóstico: esta avaliação não deve orientar treinamento automaticamente.</p>}
      <p className="hint">Exibindo até 10 candidatos. Empates têm a mesma posição; a ordem entre empatados não indica superioridade musical. Parâmetros diferentes podem produzir a mesma música.</p>
      {!details.candidates.length&&<p>Nenhum candidato avaliado com sucesso nesta geração.</p>}
      {details.candidates.map(candidate=><details key={candidate.id} className="candidate-detail"><summary>Posição {candidate.rank} · Pontuação {number(candidate.score)} · {candidate.id}</summary>
        <p>{candidate.output_notes} notas na proposta. Divisão das mãos na nota MIDI {candidate.config.split_pitch}; até {candidate.config.max_notes_per_hand} notas simultâneas por mão; alcance de {candidate.config.max_span} semitons.</p>
        <div className="metric-table" tabIndex={0} role="region" aria-label={`Critérios de ${candidate.id}`}><table><caption>Como a pontuação foi calculada</caption><thead><tr><th scope="col">Critério</th><th scope="col">Resultado</th><th scope="col">Peso</th><th scope="col">Contribuição</th></tr></thead><tbody>{criteria.map(([key,label])=><tr key={key}><th scope="row">{label}</th><td>{number(candidate.criteria[key])}</td><td>{number(details.weights[key])}</td><td>{number(candidate.contributions[key])}</td></tr>)}</tbody></table></div>
        <p className="hint">Contribuição = resultado × peso. A soma das contribuições forma a pontuação geral; os valores exibidos são arredondados.</p>
      </details>)}
      <p className="hint">Esses critérios ainda não avaliam expressividade nem reconhecem isoladamente a melodia principal. Nenhuma nova avaliação ou renderização foi executada nesta consulta.</p>
    </>}
  </section>;
}
