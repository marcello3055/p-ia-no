import { useEffect, useState } from 'react';
type Metric = { precision: number; recall: number; f1: number };
type Report = {
  config: {time_unit: string};
  counts: {reference: number; candidate: number; matched_pitch_onset: number; matched_with_duration: number; excluded_reference: number; excluded_candidate: number};
  pitch_inventory_only: Metric; pitch_and_onset: Metric; pitch_onset_and_duration: Metric;
  matched_errors: {onset_mae: number | null; duration_mae: number | null; sample_count: number};
  unmatched_reference_indices: number[]; unmatched_candidate_indices: number[];
  pitch_class_diagnostics: {global_distribution_overlap: number | null; temporal_pitch_class_jaccard: number | null};
  rhythm_diagnostics: {reference_attack_count: number; candidate_attack_count: number; matched_attacks: number; f1: number; relative_interval_similarity: number | null; relative_interval_unavailable_reason: string | null};
  warnings: string[]; limitations: string[];
  files?: {reference: string; candidate: string};
};
const percentage = (value: number) => `${(value * 100).toFixed(1)}%`;
export function MidiCompare() {
  const [reference, setReference] = useState<File | null>(null);
  const [candidate, setCandidate] = useState<File | null>(null);
  const [unit, setUnit] = useState('quarters');
  const [onset, setOnset] = useState('0.1');
  const [duration, setDuration] = useState('0.1');
  const [relative, setRelative] = useState('0.2');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [report, setReport] = useState<Report | null>(null);
  const [download, setDownload] = useState('');
  useEffect(() => {
    if (!report) { setDownload(''); return; }
    const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], {type: 'application/json'}));
    setDownload(url); return () => URL.revokeObjectURL(url);
  }, [report]);
  function reset() { setReport(null); setError(''); }
  function pick(event: React.ChangeEvent<HTMLInputElement>, setter: (file: File | null) => void) {
    reset(); setter(null);
    const file = event.target.files?.[0];
    if (!file) return;
    if (!/\.(mid|midi)$/i.test(file.name) || !file.size || file.size > 5 * 1024**2) {
      setError('Escolha um MIDI (.mid ou .midi) não vazio de até 5 MiB.'); event.target.value = ''; return;
    }
    setter(file);
  }
  async function compare() {
    if (!reference || !candidate) return;
    reset();
    const numbers = [onset, duration, relative].map(Number);
    if ([onset,duration,relative].some(v => !v.trim()) || numbers.some(v => !Number.isFinite(v) || v < 0) || numbers[0] > 10 || numbers[1] > 10 || numbers[2] > 1) {
      setError('Use tolerâncias entre 0 e 10 e uma fração de duração entre 0 e 1.'); return;
    }
    setBusy(true);
    try {
      const query = new URLSearchParams({reference_bytes: String(reference.size), time_unit: unit,
        onset_tolerance: onset, duration_tolerance: duration, duration_relative: relative});
      const response = await fetch(`/api/midi/compare?${query}`, {method:'POST',
        headers:{'Content-Type':'application/octet-stream'}, body:new Blob([reference,candidate]), signal:AbortSignal.timeout(60000)});
      const result = await response.json();
      if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'Não foi possível comparar os MIDIs. Confira arquivos e parâmetros.');
      setReport({...result, files:{reference:reference.name,candidate:candidate.name}});
    } catch(e) {
      setError(e instanceof Error && e.name === 'TimeoutError' ? 'A comparação demorou demais. Tente arquivos menores.' : e instanceof Error ? e.message : 'Falha de comunicação. Tente novamente.');
    } finally { setBusy(false); }
  }
  const label = unit === 'quarters' ? 'semínimas' : 'segundos';
  return <section className="midi-compare" aria-labelledby="midi-heading">
    <p className="eyebrow">AVALIAÇÃO EXPERIMENTAL</p><h2 id="midi-heading">Comparar dois MIDIs</h2>
    <p>Compare um arranjo de referência com um candidato. Os arquivos são enviados para análise, mas não ficam salvos. Este recurso não aceita MP3 e não gera piano.</p>
    <fieldset disabled={busy}><legend>Arquivos e tolerâncias</legend><div className="audio-grid">
      <label>Referência MIDI<input type="file" accept=".mid,.midi" onChange={event => pick(event,setReference)}/></label>
      <label>Candidato MIDI<input type="file" accept=".mid,.midi" onChange={event => pick(event,setCandidate)}/></label>
    </div><p className="hint">Até 5 MiB por arquivo. MIDI tipo 0/1. Canal de percussão excluído.</p>
    <div className="midi-options"><label>Comparar o tempo em<select value={unit} onChange={event => {reset();setUnit(event.target.value);}}><option value="quarters">Semínimas (posição musical)</option><option value="seconds">Segundos (tempo da execução)</option></select></label>
    <label>Tolerância de início ({label})<input type="number" min="0" max="10" step="0.01" value={onset} onChange={event => {reset();setOnset(event.target.value);}}/></label>
    <label>Tolerância de duração ({label})<input type="number" min="0" max="10" step="0.01" value={duration} onChange={event => {reset();setDuration(event.target.value);}}/></label>
    <label>Fração da duração de referência<input type="number" min="0" max="1" step="0.01" value={relative} onChange={event => {reset();setRelative(event.target.value);}}/></label></div>
    <p className="hint">Para a duração, vale a maior tolerância: a absoluta ou a fração da duração de referência. Ex.: 0,2 corresponde a 20%. Não há alinhamento automático de introduções ou rubato.</p>
    <button className="secondary" disabled={!reference || !candidate} onClick={compare}>Comparar MIDIs</button></fieldset>
    {busy && <p role="status">Enviando e comparando os arquivos…</p>}{error && <p role="alert" className="error">{error}</p>}
    {report && <div className="midi-result"><h3>Resultado da comparação</h3><p role="status">{report.counts.matched_pitch_onset} correspondências de altura e início em {report.counts.reference} notas de referência e {report.counts.candidate} notas candidatas.</p>
      <p className="hint">Referência: {report.files?.reference} · Candidato: {report.files?.candidate}</p>
      <div className="metric-table"><table><caption>Correspondência simbólica — não é uma nota de qualidade musical</caption><thead><tr><th>Critério</th><th>Precisão</th><th>Cobertura (recall)</th><th>F1</th></tr></thead><tbody>{[
        ['Alturas, ignorando o tempo',report.pitch_inventory_only],['Altura e início',report.pitch_and_onset],['Altura, início e duração',report.pitch_onset_and_duration]
      ].map(([title, metric]) => {const m = metric as Metric;return <tr key={title as string}><th>{title as string}</th><td>{percentage(m.precision)}</td><td>{percentage(m.recall)}</td><td>{percentage(m.f1)}</td></tr>;})}</tbody></table></div>
      <p className="hint">Precisão: proporção das notas candidatas com correspondência. Cobertura: proporção das notas da referência encontradas. F1 equilibra as duas.</p>
      <p>Erro médio de início: {report.matched_errors.onset_mae === null ? 'sem pares para calcular' : `${report.matched_errors.onset_mae.toFixed(3)} ${label}`}. Duração: {report.matched_errors.duration_mae === null ? 'sem pares para calcular' : `${report.matched_errors.duration_mae.toFixed(3)} ${label}`}.</p>
      <p className="hint">Médias calculadas somente sobre {report.matched_errors.sample_count} pares. Notas sem correspondência: {report.unmatched_reference_indices.length} na referência; {report.unmatched_candidate_indices.length} no candidato. Notas de percussão excluídas: {report.counts.excluded_reference} / {report.counts.excluded_candidate}.</p>
      <h3>Classes de altura e ritmo</h3>
      <p>Distribuição global de classes de altura: {report.pitch_class_diagnostics.global_distribution_overlap === null ? 'sem duração suficiente' : percentage(report.pitch_class_diagnostics.global_distribution_overlap)}. Coincidência temporal: {report.pitch_class_diagnostics.temporal_pitch_class_jaccard === null ? 'sem duração suficiente' : percentage(report.pitch_class_diagnostics.temporal_pitch_class_jaccard)}.</p>
      <p className="hint">Classes de altura agrupam notas de mesmo nome em oitavas diferentes. A distribuição global ignora a ordem; a coincidência temporal compara as classes ativas ao longo do tempo. Nenhuma delas reconhece função harmônica ou qualidade do arranjo.</p>
      <p>Correspondência de ataques (F1): {percentage(report.rhythm_diagnostics.f1)} — {report.rhythm_diagnostics.matched_attacks} coincidências em {report.rhythm_diagnostics.reference_attack_count} ataques de referência e {report.rhythm_diagnostics.candidate_attack_count} candidatos.</p>
      <p>Padrão relativo de intervalos entre ataques: {report.rhythm_diagnostics.relative_interval_similarity === null ? 'não calculado' : percentage(report.rhythm_diagnostics.relative_interval_similarity)}.</p>
      {report.rhythm_diagnostics.relative_interval_unavailable_reason && <p className="hint">{report.rhythm_diagnostics.relative_interval_unavailable_reason}</p>}
      <p className="hint">Notas simultâneas contam como um ataque. O padrão relativo ignora deslocamento global e mudança uniforme de andamento; não compara alturas, durações ou expressividade.</p>
      {report.warnings.map(warning => <p className="notice" key={warning}>{warning}</p>)}
      <details><summary>Limites desta avaliação</summary><ul>{report.limitations.map(item => <li key={item}>{item}</li>)}</ul></details>
      {download && <a className="backup-link" href={download} download="P-IA-NO-comparacao-MIDI.json">Baixar relatório completo (JSON)</a>}
      <p className="hint">O relatório inclui parâmetros, pares de notas e índices sem correspondência. O resultado desaparece ao recarregar a página; baixe-o para guardar.</p>
    </div>}
  </section>;
}
