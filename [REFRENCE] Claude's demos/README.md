# 🇩🇪 German Language Tutor

An AI-powered German language learning assistant that listens to your speech, provides real-time corrections, and helps you improve your German pronunciation and grammar.

##  Features

- 🎤 **Real-time Speech Recognition** - Speak German and get instant feedback
- 🧠 **AI-Powered Corrections** - Grammar checking and suggestions using LLM
- 🔊 **Text-to-Speech Feedback** - Hear correct pronunciations
- 🌐 **Bilingual Support** - Handles both German and English input
- ⚡ **GPU Acceleration** - Optional CUDA support for local models
- 🆓 **Flexible API Options** - Works with OpenAI, free APIs, or offline mode

---

##  Quick Start

### Prerequisites

- Python 3.8+
- Microphone access
- Internet connection (for speech recognition and API features)
- Optional: NVIDIA GPU with CUDA (for local models)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/german-tutor.git
cd german-tutor
```

2. **Create virtual environment:**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt

# Windows users may need:
pip install pipwin
pipwin install pyaudio
```

4. **Test your setup:**
```bash
python test_updated_tutor.py
```

5. **Run the tutor:**
```bash
python tutor.py
```

---

##  Usage

### Voice Mode (Recommended)
```bash
python claude_tutor.py
# Select option 1: Voice mode
# Speak German phrases and receive instant feedback
```

Example session:
```
🎤 You said: 'Ich bin gut'
📝 Feedback:
   ✏️  Correction: Mir geht es gut
   🔤 Translation: I am doing well  
   📚 Grammar: 'Ich bin gut' is literal. 'Mir geht es gut' is more natural German.
```

### Text Mode
```bash
python claude_tutor.py
# Select option 2: Text mode
# Type German sentences for correction
```

### Microphone Test
```bash
python mic_test.py
# Comprehensive microphone testing and diagnostics
```

---

## Configuration

### API Setup (Recommended for best accuracy)

#### Option 1: OpenAI API
```python
# In tutor.py, update:
OPENAI_API_KEY = "your-openai-api-key-here"
```

#### Option 2: Free Alternatives
- **Together AI**: Free tier available at [together.ai](https://together.ai)
- **Hugging Face**: Free inference API at [huggingface.co](https://huggingface.co)

#### Option 3: Offline Mode
The tutor works offline with basic rule-based corrections (limited accuracy).

### Hardware Optimization

#### For NVIDIA GPUs:
```bash
# Install CUDA-enabled PyTorch (optional, only needed for local LLM)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### For RTX 3060 users:
The system is optimized for 12GB VRAM and will automatically use GPU when available.

---

##  Technical Details

### Architecture
- **Speech-to-Text**: Google Speech Recognition API (German/English)
- **Language Processing**: OpenAI GPT-3.5 or local transformer models
- **Text-to-Speech**: System TTS with German voice support
- **GPU Support**: Optional CUDA acceleration for local models

### Dependencies
- `speech_recognition` - Audio input and Google Speech API
- `pyttsx3` - Text-to-speech output
- `openai` - LLM API integration (optional)
- `torch` - Local model support (optional)
- `transformers` - Hugging Face model integration (optional)

---

##  Troubleshooting

### Common Issues

#### "No microphones found"
```bash
# Check Windows microphone permissions:
# Settings → Privacy → Microphone → Allow desktop apps

# List available microphones:
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

#### "Speech recognition failed"
- Ensure internet connection (required for Google Speech API)
- Check microphone volume levels
- Try speaking closer to the microphone
- Run `python mic_test.py` for detailed diagnostics

#### "PyAudio installation failed"
```bash
# Windows:
pip install pipwin
pipwin install pyaudio

# Linux:
sudo apt-get install portaudio19-dev python3-pyaudio

# Mac:
brew install portaudio
pip install pyaudio
```

#### API errors
- Verify your API key is correct
- Check API quota/billing status
- Test with offline mode first

### Performance Tips

1. **For best accuracy**: Use OpenAI API
2. **For privacy**: Use local models with CUDA GPU
3. **For speed**: Use basic offline mode
4. **For testing**: Start with text mode before voice mode

---

## 📊 Supported Features by Mode

| Feature | Offline Mode | API Mode | Local GPU Mode |
|---------|--------------|----------|----------------|
| Speech Recognition | ✅ | ✅ | ✅ |
| Basic Grammar Check | ✅ | ✅ | ✅ |
| Advanced Corrections | ❌ | ✅ | ⚠️ Limited |
| Detailed Explanations | ❌ | ✅ | ⚠️ Limited |
| Custom Learning | ❌ | ✅ | ✅ |
| Privacy | ✅ | ❌ | ✅ |
