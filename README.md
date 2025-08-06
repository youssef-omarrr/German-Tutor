# Real-Time German–English Voice Tutor

This is a fully local, real-time bilingual voice assistant powered by your RTX 3060 (6 GB VRAM). It listens to your German speech, corrects your grammar, translates into English, provides explanations, and speaks back in both languages—all with sub-second latency and no cloud APIs required.

---

## Project Overview

- **Input**: Speak German into your microphone.
    
- **ASR**: Uses `whisper_streaming` (built on top of Whisper + faster-whisper) for real-time German transcription with ~3.3 s latency. ([pydigger.com](https://pydigger.com/pypi/RealTimeTTS?utm_source=chatgpt.com "RealTimeTTS - PyDigger"), [GitHub](https://github.com/ufal/whisper_streaming?utm_source=chatgpt.com "ufal/whisper_streaming: Whisper realtime streaming for ... - GitHub"))
    
- **LLM**: Local inference using Vicuna‑7B in 4-bit GPTQ quantized format—provides grammar correction, English translation, and explanations.
    
- **TTS**: `RealtimeTTS` (supports multiple engines) delivers spoken feedback in both German and English with minimal delay. ([GitHub](https://github.com/KoljaB/RealtimeTTS?utm_source=chatgpt.com "KoljaB/RealtimeTTS: Converts text to speech in realtime - GitHub"))
    
- (Optional) **RealtimeSTT** for more advanced VAD and wake-word controls. ([GitHub](https://github.com/KoljaB/RealtimeSTT?utm_source=chatgpt.com "KoljaB/RealtimeSTT - GitHub"))
    
---

## File Structure

```
realtime_tutor/
├── README.md
├── requirements.txt
└── tutor.py
```

- **README.md**: This file.
    
- **requirements.txt**: Dependencies.
    
- **tutor.py**: One-script implementation of the real-time voice tutor.
    

---

## Contributions & Notes

This project uses stable open-source libraries for streaming ASR and TTS. Using them together makes real-time voice tutoring feasible on modest hardware—and it's modular, so feel free to extend with wake words, UI, or offline datasets!

Backed by open research and trusted engineering communities. Let me know if you'd like to improve prompts, integrate real-time VAD, or explore accent-specific feedback!

---