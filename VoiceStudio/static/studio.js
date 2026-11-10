// VoiceStudio Studio JavaScript Engine
// Pure Vanilla ES6 - Zero Framework Overhead

document.addEventListener('DOMContentLoaded', () => {
  const state = {
    selectedVoiceId: null,
    audioContext: null,
    audioBuffer: null,
    audioElement: new Audio(),
    isPlaying: false,
    duration: 0,
    currentAudioUrl: null,
  };

  // Elements
  const scriptInput = document.getElementById('scriptInput');
  const speedSlider = document.getElementById('speedSlider');
  const speedVal = document.getElementById('speedVal');
  const pitchSlider = document.getElementById('pitchSlider');
  const pitchVal = document.getElementById('pitchVal');
  const synthesizeBtn = document.getElementById('synthesizeBtn');
  const progressBar = document.getElementById('progressBar');
  const progressSection = document.getElementById('progressSection');
  const progressStatusText = document.getElementById('progressStatusText');
  const progressPercentage = document.getElementById('progressPercentage');
  const progressSubtext = document.getElementById('progressSubtext');
  const progressSpinner = document.getElementById('progressSpinner');
  const profilesList = document.getElementById('profilesList');
  const dropzone = document.getElementById('dropzone');
  const audioFileInput = document.getElementById('audioFileInput');
  const playBtn = document.getElementById('playBtn');
  const canvas = document.getElementById('waveformCanvas');
  const ctx = canvas.getContext('2d');
  const snrReadout = document.getElementById('snrReadout');
  const lufsReadout = document.getElementById('lufsReadout');
  const peakReadout = document.getElementById('peakReadout');
  const downloadBtn = document.getElementById('downloadBtn');

  function resizeCanvas() {
    canvas.width = canvas.parentElement.clientWidth * window.devicePixelRatio;
    canvas.height = canvas.parentElement.clientHeight * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    drawWaveform();
  }
  window.addEventListener('resize', resizeCanvas);

  speedSlider.addEventListener('input', (e) => {
    speedVal.textContent = parseFloat(e.target.value).toFixed(2) + 'x';
  });
  pitchSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    pitchVal.textContent = (val > 0 ? '+' : '') + val.toFixed(1) + ' st';
  });

  async function loadInitialData() {
    try {
      const healthRes = await fetch('/api/health');
      const health = await healthRes.json();
      document.getElementById('engineBadge').textContent = health.engines[0]?.engine_name || 'pytorch_cpu';
      document.getElementById('srBadge').textContent = health.sample_rate + ' Hz';
      document.getElementById('deviceBadge').textContent = health.device.toUpperCase();

      await loadVoiceProfiles();
    } catch (err) {
      console.error('Initialization error:', err);
    }
  }

  async function loadVoiceProfiles() {
    try {
      const res = await fetch('/api/voices');
      const profiles = await res.json();
      profilesList.innerHTML = '';

      if (profiles.length === 0) {
        profilesList.innerHTML = '<div style="padding: 12px; color: var(--text-muted); font-size: 12px;">No voice profiles registered. Drop an audio sample below to clone.</div>';
        return;
      }

      profiles.forEach((p, idx) => {
        const card = document.createElement('div');
        card.className = 'profile-card' + (p.id === state.selectedVoiceId || (!state.selectedVoiceId && idx === 0) ? ' selected' : '');
        if (!state.selectedVoiceId && idx === 0) {
          state.selectedVoiceId = p.id;
        }

        card.innerHTML = `
          <div class="profile-name">
            <span>${p.name}</span>
            <span style="font-size: 11px; color: var(--text-muted);">${p.language.toUpperCase()}</span>
          </div>
          <div class="profile-desc">${p.description || 'Conditioned zero-shot profile'}</div>
        `;

        card.addEventListener('click', () => {
          document.querySelectorAll('.profile-card').forEach(c => c.classList.remove('selected'));
          card.classList.add('selected');
          state.selectedVoiceId = p.id;
        });

        profilesList.appendChild(card);
      });
    } catch (err) {
      console.error('Failed to load profiles:', err);
    }
  }

  dropzone.addEventListener('click', () => audioFileInput.click());
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
  dropzone.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      await uploadReferenceAudio(e.dataTransfer.files[0]);
    }
  });

  audioFileInput.addEventListener('change', async (e) => {
    if (e.target.files.length > 0) {
      await uploadReferenceAudio(e.target.files[0]);
    }
  });

  function setProgress(pct, stage, sub) {
    if (progressBar) progressBar.style.width = pct + '%';
    if (progressPercentage) progressPercentage.textContent = pct + '%';
    if (stage && progressStatusText) progressStatusText.textContent = stage;
    if (sub && progressSubtext) progressSubtext.textContent = sub;
  }

  async function uploadReferenceAudio(file) {
    const formData = new FormData();
    const name = prompt('Voice Profile Name:', file.name.replace(/\.[^/.]+$/, '')) || 'Uploaded Voice';
    formData.append('name', name);
    formData.append('description', 'Reference voice recording');
    formData.append('file', file);

    if (progressSection) progressSection.style.display = 'flex';
    if (progressSpinner) progressSpinner.style.display = 'inline-block';
    setProgress(30, 'Uploading audio sample...', 'Extracting acoustic embeddings');

    try {
      const res = await fetch('/api/voices/upload', {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        setProgress(100, 'Voice enrolled successfully!', `Profile "${name}" ready to synthesize`);
        if (progressSpinner) progressSpinner.style.display = 'none';
        await loadVoiceProfiles();
      } else {
        const err = await res.json();
        alert('Upload failed: ' + err.detail);
        setProgress(0, 'Upload failed', err.detail);
      }
    } catch (err) {
      alert('Error uploading voice reference: ' + err.message);
      setProgress(0, 'Upload error', err.message);
    }
  }

  synthesizeBtn.addEventListener('click', handleSynthesize);
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
      handleSynthesize();
    }
    if (e.code === 'Space' && e.target.tagName !== 'TEXTAREA') {
      e.preventDefault();
      togglePlayback();
    }
  });

  async function handleSynthesize() {
    const text = scriptInput.value.trim();
    if (!text) return;

    const jobId = 'synth_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7);
    synthesizeBtn.disabled = true;

    // Show progress section
    if (progressSection) progressSection.style.display = 'flex';
    if (progressSpinner) progressSpinner.style.display = 'inline-block';
    setProgress(5, 'Initializing synthesis pipeline...', 'CPU Inference Active');

    let sse = null;
    let pollInterval = null;
    let sseActive = true;

    try {
      sse = new EventSource(`/api/synthesize/sse?job_id=${jobId}&text=${encodeURIComponent(text)}`);
      sse.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.progress_pct !== undefined) {
            setProgress(data.progress_pct, data.stage || 'Synthesizing voice...', data.word ? `Word: ${data.word}` : null);
          }
          if (data.status === 'completed' || data.progress_pct >= 100) {
            sseActive = false;
            sse.close();
          }
        } catch (e) {
          console.warn('SSE parse error:', e);
        }
      };
      sse.onerror = () => {
        if (sse) sse.close();
        sseActive = false;
      };
    } catch (e) {
      console.warn('SSE connection failed, falling back to polling:', e);
      sseActive = false;
    }

    // Polling fallback to ensure smooth updates even if SSE is buffered
    pollInterval = setInterval(async () => {
      if (!sseActive) {
        try {
          const res = await fetch(`/api/synthesize/progress/${jobId}`);
          if (res.ok) {
            const data = await res.json();
            if (data.progress_pct !== undefined && data.progress_pct > 0) {
              setProgress(data.progress_pct, data.stage);
            }
            if (data.status === 'completed' || data.progress_pct >= 100) {
              clearInterval(pollInterval);
            }
          }
        } catch (_) {}
      }
    }, 200);

    try {
      const res = await fetch('/api/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: jobId,
          text: text,
          voice_profile_id: state.selectedVoiceId,
          speed: parseFloat(speedSlider.value),
          pitch: parseFloat(pitchSlider.value),
          normalize_loudness: true,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        alert('Synthesis error: ' + (err.detail || 'Unknown error'));
        setProgress(0, 'Synthesis failed', err.detail);
        return;
      }

      const record = await res.json();
      setProgress(100, 'Speech synthesis complete!', `Output saved: ${record.duration_sec}s (${record.sample_rate}Hz)`);
      if (progressSpinner) progressSpinner.style.display = 'none';

      await loadGeneratedAudio(record.output_audio_path, record.quality_metrics);
    } catch (err) {
      console.error('Synthesis request failed:', err);
      setProgress(0, 'Synthesis error', err.message);
    } finally {
      if (sse) sse.close();
      if (pollInterval) clearInterval(pollInterval);
      synthesizeBtn.disabled = false;
    }
  }

  async function loadGeneratedAudio(filePath, metrics) {
    const filename = filePath.split(/[\\/]/).pop();
    state.currentAudioUrl = `/api/audio/${filename}`;
    state.audioElement.src = state.currentAudioUrl;

    if (downloadBtn) {
      downloadBtn.onclick = () => {
        window.open(state.currentAudioUrl, '_blank');
      };
    }

    if (metrics) {
      snrReadout.textContent = metrics.snr_db.toFixed(1) + ' dB';
      lufsReadout.textContent = metrics.integrated_lufs.toFixed(1) + ' LUFS';
      peakReadout.textContent = (metrics.peak_amplitude * 100).toFixed(0) + '%';
    }

    const res = await fetch(state.currentAudioUrl);
    const arrayBuf = await res.arrayBuffer();
    if (!state.audioContext) {
      state.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    state.audioBuffer = await state.audioContext.decodeAudioData(arrayBuf);
    state.duration = state.audioBuffer.duration;
    drawWaveform();
  }

  function drawWaveform() {
    const width = canvas.parentElement.clientWidth;
    const height = canvas.parentElement.clientHeight;
    ctx.clearRect(0, 0, width, height);

    if (!state.audioBuffer) {
      ctx.strokeStyle = '#30363d';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, height / 2);
      ctx.lineTo(width, height / 2);
      ctx.stroke();
      return;
    }

    const channelData = state.audioBuffer.getChannelData(0);
    const step = Math.ceil(channelData.length / width);
    const amp = height / 2;

    ctx.fillStyle = '#6366f1';
    for (let i = 0; i < width; i++) {
      let min = 1.0;
      let max = -1.0;
      for (let j = 0; j < step; j++) {
        const datum = channelData[i * step + j];
        if (datum < min) min = datum;
        if (datum > max) max = datum;
      }
      ctx.fillRect(i, (1 + min) * amp, 1, Math.max(1, (max - min) * amp));
    }

    if (state.duration > 0) {
      const progress = state.audioElement.currentTime / state.duration;
      const x = progress * width;
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
  }

  state.audioElement.addEventListener('timeupdate', () => {
    drawWaveform();
  });
  state.audioElement.addEventListener('ended', () => {
    state.isPlaying = false;
    playBtn.textContent = '▶';
  });

  playBtn.addEventListener('click', togglePlayback);

  function togglePlayback() {
    if (!state.audioElement.src) return;
    if (state.isPlaying) {
      state.audioElement.pause();
      state.isPlaying = false;
      playBtn.textContent = '▶';
    } else {
      state.audioElement.play();
      state.isPlaying = true;
      playBtn.textContent = '⏸';
    }
  }

  canvas.addEventListener('click', (e) => {
    if (!state.duration) return;
    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const pct = clickX / rect.width;
    state.audioElement.currentTime = pct * state.duration;
    drawWaveform();
  });

  resizeCanvas();
  loadInitialData();
});
