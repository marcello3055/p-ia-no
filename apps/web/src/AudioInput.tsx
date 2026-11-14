import { useEffect, useRef, useState } from 'react';
export function AudioInput({ id, title }: { id: string; title: string }) {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [ready, setReady] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  const audio = useRef<HTMLAudioElement>(null);
  useEffect(() => {
    if (!file) { setUrl(''); return; }
    const objectUrl = URL.createObjectURL(file);
    setUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);
  function clear() {
    audio.current?.pause(); setFile(null); setReady(false); setError('');
    if (input.current) input.current.value = '';
  }
  return <article className="audio-card">
    <h3>{title}</h3>
    <label className="file-label" htmlFor={id}>Selecionar áudio</label>
    <input ref={input} id={id} type="file" accept=".mp3,.wav,.flac,audio/mpeg,audio/wav,audio/flac" aria-describedby={`${id}-help`} onChange={event => {
      const chosen = event.target.files?.[0];
      if (!chosen) return;
      audio.current?.pause(); setReady(false); setError(''); setFile(null);
      if (!/\.(mp3|wav|flac)$/i.test(chosen.name)) { setError('Selecione um arquivo MP3, WAV ou FLAC.'); event.target.value = ''; return; }
      if (!chosen.size || chosen.size > 100 * 1024 * 1024) { setError('Selecione um arquivo não vazio de até 100 MB.'); event.target.value = ''; return; }
      setFile(chosen);
    }}/>
    <p id={`${id}-help`} className="hint">MP3, WAV ou FLAC · até 100 MB · reprodução local</p>
    {file && <div className="selected"><p className="filename">{file.name}</p><p className="hint">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
      {url && <audio key={url} ref={audio} controls preload="metadata" src={url} aria-label={`Ouvir ${title.toLowerCase()}`} onLoadedMetadata={() => { setReady(true); setError(''); }} onError={() => { setReady(false); setError('Não foi possível reproduzir este arquivo. Ele pode estar danificado ou usar um codec incompatível.'); }} onPlay={event => {
        document.querySelectorAll('audio').forEach(other => { if (other !== event.currentTarget) other.pause(); });
      }}/>}<p className="hint" role="status">{ready ? 'Pronto para ouvir. Este é o arquivo original, sem alterações.' : error ? '' : 'Verificando se o navegador consegue reproduzir…'}</p><button className="secondary" onClick={clear}>Remover arquivo</button></div>}
    {error && <p className="error" role="alert">{error}</p>}
  </article>;
}
