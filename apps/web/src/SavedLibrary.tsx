import { useEffect, useState } from 'react';
type AudioRecord = { id: string; name: string; size: number; duration: number; created_at: string };
type PairRecord = { id: string; name: string; base_id: string; reference_id: string };
async function jsonRequest(path: string, options?: RequestInit) {
  const response = await fetch(path, { ...options, signal: AbortSignal.timeout(15000), cache: 'no-store' });
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Não foi possível concluir a operação.');
  return data;
}
function upload(file: File, progress: (text: string) => void): Promise<AudioRecord> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `/api/audio?filename=${encodeURIComponent(file.name)}`);
    xhr.setRequestHeader('Content-Type', 'application/octet-stream');
    xhr.timeout = 120000;
    xhr.upload.onprogress = event => {
      if (event.lengthComputable) progress(`${file.name}: ${Math.round(event.loaded / event.total * 100)}% enviado`);
    };
    xhr.upload.onload = () => progress(`${file.name}: validando no servidor…`);
    xhr.onload = () => {
      try {
        const data = JSON.parse(xhr.responseText);
        if (xhr.status < 200 || xhr.status >= 300) throw new Error(typeof data.detail === 'string' ? data.detail : 'Falha ao salvar áudio.');
        resolve(data);
      } catch (error) { reject(error); }
    };
    xhr.onerror = () => reject(new Error('Conexão interrompida. Verifique a biblioteca antes de tentar novamente.'));
    xhr.ontimeout = () => reject(new Error('O envio demorou demais. Verifique a biblioteca e tente novamente.'));
    xhr.send(file);
  });
}
function SavedPlayer({ id, label }: { id: string; label: string }) {
  const [failed, setFailed] = useState(false);
  return <div><p className="hint">{label}</p><audio controls preload="none" src={`/api/audio/${id}/content`} aria-label={label} onError={() => setFailed(true)} onPlay={event => {
    document.querySelectorAll('audio').forEach(other => { if (other !== event.currentTarget) other.pause(); });
  }}/>{failed && <p className="error">Arquivo indisponível ou incompatível com este navegador.</p>}</div>;
}
export function SavedLibrary({ mode, first, second }: { mode: 'pairs' | 'audio'; first: File | null; second?: File | null }) {
  const [name, setName] = useState('');
  const [audios, setAudios] = useState<AudioRecord[]>([]);
  const [pairs, setPairs] = useState<PairRecord[]>([]);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  async function refresh() {
    setLoading(true);
    try {
      const [audioData, pairData] = await Promise.all([jsonRequest('/api/audio'), jsonRequest('/api/pairs')]);
      setAudios(audioData); setPairs(pairData);
    } finally { setLoading(false); }
  }
  useEffect(() => { refresh().catch(() => setError('Não foi possível carregar os arquivos salvos. Use Atualizar lista para tentar novamente.')); }, []);
  async function save() {
    if (!first || (mode === 'pairs' && (!second || !name.trim()))) return;
    setBusy(true); setError(''); setStatus('Iniciando envio…');
    try {
      const base = await upload(first, setStatus);
      if (mode === 'pairs' && second) {
        const reference = await upload(second, setStatus);
        await jsonRequest('/api/pairs', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name.trim(), base_id: base.id, reference_id: reference.id }) });
      }
      setStatus(mode === 'pairs' ? 'Par salvo no ambiente de desenvolvimento.' : 'Áudio salvo no ambiente de desenvolvimento.');
      await refresh();
    } catch (e) {
      setStatus('');
      setError(`${e instanceof Error ? e.message : 'Falha ao salvar.'} Um áudio já enviado pode ter sido preservado; uma nova tentativa reutiliza o mesmo conteúdo.`);
    } finally { setBusy(false); }
  }
  return <section className="saved-library" aria-label={mode === 'pairs' ? 'Pares salvos' : 'Áudios salvos'}>
    {mode === 'pairs' && <label className="pair-name">Nome do par<input type="text" value={name} maxLength={120} disabled={busy} onChange={event => setName(event.target.value)} placeholder="Ex.: Tema principal — versão para piano"/></label>}
    <div className="save-actions"><button className="secondary" onClick={save} disabled={busy || !first || (mode === 'pairs' && (!second || !name.trim()))}>{busy ? 'Salvando…' : mode === 'pairs' ? 'Salvar par no servidor' : 'Salvar áudio no servidor'}</button><button className="secondary" disabled={busy || loading} onClick={() => { setError(''); refresh().catch(() => setError('Não foi possível atualizar a lista.')); }}>Atualizar lista</button></div>
    <p className="hint">Salvar envia os arquivos ao servidor de desenvolvimento. Limites: 100 MiB por arquivo, 30 minutos e 1 GiB no total. Conteúdo idêntico é reutilizado. Ainda não há backup externo.</p>
    {status && <p role="status">{status}</p>}{error && <p className="error" role="alert">{error}</p>}
    <h3>{mode === 'pairs' ? 'Pares salvos' : 'Áudios salvos (inclui os exemplos de treinamento)'}</h3>
    {loading ? <p role="status">Carregando biblioteca…</p> : mode === 'pairs' ? pairs.length ? pairs.map(pair => <article className="audio-card" key={pair.id}><h4>{pair.name}</h4><div className="audio-grid"><SavedPlayer id={pair.base_id} label="Ouvir orquestra salva"/><SavedPlayer id={pair.reference_id} label="Ouvir piano de referência salvo"/></div></article>) : <p className="hint">Nenhum par salvo.</p> : audios.length ? audios.map(audio => <article className="audio-card" key={audio.id}><h4 className="filename">{audio.name}</h4><p className="hint">{Math.round(audio.duration)} s · {(audio.size / 1024**2).toFixed(2)} MiB</p><SavedPlayer id={audio.id} label={`Ouvir ${audio.name}`}/></article>) : <p className="hint">Nenhum áudio salvo.</p>}
  </section>;
}
