document.addEventListener('DOMContentLoaded', () => {
  const urlInput = document.getElementById('media-url');
  const pasteBtn = document.getElementById('paste-btn');
  const analyzeBtn = document.getElementById('analyze-btn');
  const openMusicFolderBtn = document.getElementById('open-music-folder-btn');
  const openVideoFolderBtn = document.getElementById('open-video-folder-btn');

  const previewSection = document.getElementById('preview-section');
  const videoThumbnail = document.getElementById('video-thumbnail');
  const videoDuration = document.getElementById('video-duration');
  const videoTitle = document.getElementById('video-title');
  const videoArtist = document.getElementById('video-artist');
  const originalResolutionBadge = document.getElementById('original-resolution-badge');
  const originalQualityBadge = document.getElementById('original-quality-badge');
  const modeCards = document.querySelectorAll('.mode-card');
  const downloadBtn = document.getElementById('download-btn');

  const progressSection = document.getElementById('progress-section');
  const statusText = document.getElementById('status-text');
  const progressPercentage = document.getElementById('progress-percentage');
  const progressBar = document.getElementById('progress-bar');

  const resultSection = document.getElementById('result-section');
  const metricScore = document.getElementById('metric-score');
  const metricBitrate = document.getElementById('metric-bitrate');
  const metricSampleRate = document.getElementById('metric-sample-rate');
  const metricSize = document.getElementById('metric-size');
  const audioPlayer = document.getElementById('audio-player');
  const playerWaveform = document.querySelector('.player-waveform');

  const errorModal = document.getElementById('error-modal');
  const errorModalBody = document.getElementById('error-modal-body');
  const closeModalBtn = document.getElementById('close-modal-btn');

  let currentUrl = '';
  let selectedMode = 'audio';

  function showErrorModal(message) {
    errorModalBody.textContent = message || 'خطایی رخ داد.';
    errorModal.classList.remove('hidden');
  }

  closeModalBtn.addEventListener('click', () => {
    errorModal.classList.add('hidden');
  });

  // Audio player play/pause waveform animation hook
  audioPlayer.addEventListener('play', () => {
    playerWaveform.classList.add('playing');
  });

  audioPlayer.addEventListener('pause', () => {
    playerWaveform.classList.remove('playing');
  });

  audioPlayer.addEventListener('ended', () => {
    playerWaveform.classList.remove('playing');
  });

  // Mode Selection Cards
  modeCards.forEach(card => {
    card.addEventListener('click', () => {
      modeCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      selectedMode = card.getAttribute('data-mode') || 'audio';
    });
  });

  // Paste clipboard content
  pasteBtn.addEventListener('click', async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        urlInput.value = text.trim();
        analyzeUrl();
      }
    } catch (err) {
      console.warn('Clipboard read error:', err);
    }
  });

  // Open Music Folder
  openMusicFolderBtn.addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.open_music_folder();
    }
  });

  // Open Video Folder
  openVideoFolderBtn.addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.open_video_folder();
    }
  });

  // Analyze URL
  analyzeBtn.addEventListener('click', () => analyzeUrl());
  urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') analyzeUrl();
  });

  async function analyzeUrl() {
    const url = urlInput.value.trim();
    if (!url) return;

    currentUrl = url;
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '🔄 در حال آنالیز...';
    resultSection.classList.add('hidden');

    try {
      let data;
      if (window.pywebview && window.pywebview.api) {
        data = await window.pywebview.api.probe_url(url);
      } else {
        data = {
          success: true,
          title: 'Sample Video Media',
          uploader: 'Media Uploader',
          duration: 213,
          thumbnail: 'https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg',
          best_resolution: '1080p Full HD',
          best_abr: '320 kbps (MP3)'
        };
      }

      if (data && data.success) {
        videoThumbnail.src = data.thumbnail || '';
        videoTitle.textContent = data.title || 'عنوان رسانه';
        videoArtist.textContent = data.uploader || 'نام کانال';
        
        const minutes = Math.floor((data.duration || 0) / 60);
        const seconds = Math.floor((data.duration || 0) % 60);
        videoDuration.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

        originalResolutionBadge.textContent = `🎬 ویدیو: ${data.best_resolution || '1080p'}`;
        originalQualityBadge.textContent = `🎵 صدا: ${data.best_abr || '320 kbps'}`;

        previewSection.classList.remove('hidden');
      } else {
        showErrorModal(data.error || 'نمی‌توان اطلاعات رسانه را بازخوانی کرد.');
      }
    } catch (err) {
      console.error(err);
      showErrorModal('خطا در بررسی لینک رسانه.');
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = '🔍 آنالیز لینک';
    }
  }

  // Start Download
  downloadBtn.addEventListener('click', async () => {
    if (!currentUrl) return;

    downloadBtn.disabled = true;
    downloadBtn.innerHTML = '⚡️ در حال دریافت رسانه...';
    progressSection.classList.remove('hidden');
    resultSection.classList.add('hidden');

    statusText.textContent = `در حال دریافت رسانه در حالت: ${selectedMode}...`;
    progressBar.style.width = '35%';
    progressPercentage.textContent = '35%';

    try {
      let res;
      if (window.pywebview && window.pywebview.api) {
        res = await window.pywebview.api.download_media(currentUrl, selectedMode);
      } else {
        res = {
          success: true,
          type: selectedMode,
          quality: {
            quality_score: '🔥 فوق‌العاده (320 kbps / 1080p)',
            bitrate_kbps: 320,
            sample_rate_hz: 44100,
            file_size_mb: 12.4
          },
          audio_url: ''
        };
      }

      if (res && res.success) {
        progressBar.style.width = '100%';
        progressPercentage.textContent = '100%';
        statusText.textContent = '✅ دانلود و ذخیره در پوشه کاربر با موفقیت کامل شد!';

        const q = res.quality || {};
        metricScore.textContent = q.quality_score || '🔥 عالی';
        metricBitrate.textContent = `${q.bitrate_kbps || 320} kbps`;
        metricSampleRate.textContent = `${q.sample_rate_hz || 44100} Hz`;
        metricSize.textContent = `${q.file_size_mb || 0} MB`;

        if (res.audio_url) {
          audioPlayer.src = res.audio_url;
          audioPlayer.load();
          audioPlayer.play().catch(e => console.warn('Audio play auto-trigger:', e));
        }

        resultSection.classList.remove('hidden');
      } else {
        showErrorModal(res.error || 'خطا در دریافت رسانه.');
      }
    } catch (err) {
      console.error(err);
      showErrorModal('خطا در فرایند دانلود.');
    } finally {
      downloadBtn.disabled = false;
      downloadBtn.innerHTML = '⚡️ دریافت فایل با کیفیت عالی';
    }
  });
});
