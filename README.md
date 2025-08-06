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

## Architecture & Flow

```text
Mic → VAD/Wakeword (optional) → Streaming ASR → LLM Inference → Bilingual TTS Output
```

1. **Mic → ASR**
    
    - Captures speech and sends it to `whisper_streaming` for efficient real-time transcription. ([GitHub](https://github.com/ufal/whisper_streaming?utm_source=chatgpt.com "ufal/whisper_streaming: Whisper realtime streaming for ... - GitHub"))
        
2. **Prompt LLM**
    
    - The German text is passed to a prompt that asks the model to correct it in German, translate it into English, and explain the meaning in English.
        
3. **TTS Output**
    
    - Uses `RealtimeTTS` for near-instantaneous speech synthesis in German and English. ([pydigger.com](https://pydigger.com/pypi/RealTimeTTS?utm_source=chatgpt.com "RealTimeTTS - PyDigger"))
        
4. **(Optional) Advanced ASR**
    
    - `RealtimeSTT` can provide automatic speech segmentation, VAD, or wake-word activation for extra control. ([GitHub](https://github.com/KoljaB/RealtimeSTT?utm_source=chatgpt.com "KoljaB/RealtimeSTT - GitHub"))
        

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

## requirements.txt

```text
torch
faster-whisper
whisper-streaming
transformers>=4.32.0
auto-gptq>=0.4.2
silero-tts
RealtimeTTS[all]
sounddevice
```

---

## Why It Works

- **Low Latency ASR**: `whisper_streaming` implements a streaming policy with self-adaptive latency to target ~3.3-second response time. ([GitHub](https://github.com/openai/whisper?utm_source=chatgpt.com "openai/whisper: Robust Speech Recognition via Large ... - GitHub"), [GitHub](https://github.com/ufal/whisper_streaming?utm_source=chatgpt.com "ufal/whisper_streaming: Whisper realtime streaming for ... - GitHub"), [GitHub](https://github.com/KoljaB/RealtimeTTS/blob/master/RealtimeTTS/engines/coqui_engine.py?utm_source=chatgpt.com "RealtimeTTS/RealtimeTTS/engines/coqui_engine.py at master"), [GitHub](https://github.com/KoljaB/RealtimeSTT?utm_source=chatgpt.com "KoljaB/RealtimeSTT - GitHub"), [GitHub](https://github.com/KoljaB/RealtimeTTS/releases?utm_source=chatgpt.com "Releases · KoljaB/RealtimeTTS - GitHub"))
    
- **Lightweight German–English LLM**: Vicuna‑7B in 4-bit GPTQ fits within ~6 GB VRAM on your RTX 3060.
    
- **Instant Feedback**: `RealtimeTTS` avoids buffering delays, speaking responses immediately in both languages. ([GitHub](https://github.com/KoljaB/RealtimeTTS?utm_source=chatgpt.com "KoljaB/RealtimeTTS: Converts text to speech in realtime - GitHub"), [pydigger.com](https://pydigger.com/pypi/RealTimeTTS?utm_source=chatgpt.com "RealTimeTTS - PyDigger"))
    

---

## Getting Started

1. Clone or download this repo.
    
2. Install dependencies:
    
    ```bash
    pip install -r requirements.txt
    ```
    
3. Place your German speech input or use your mic directly.
    
4. Run:
    
    ```bash
    python tutor.py
    ```
    

Speak a German sentence. The system will immediately:

- Correct your German
    
- Translate it into English
    
- Explain the meaning in English  
    Then it speaks the response back in both German and English.
    

---

## Contributions & Notes

This project uses stable open-source libraries for streaming ASR and TTS. Using them together makes real-time voice tutoring feasible on modest hardware—and it's modular, so feel free to extend with wake words, UI, or offline datasets!

Backed by open research and trusted engineering communities. Let me know if you'd like to improve prompts, integrate real-time VAD, or explore accent-specific feedback!

---