# `RealtimeSTT` vs `speech_recognition`

### `**RealtimeSTT**`

* **Pros:** Built-in hot-word support via Porcupine; integrated console spinners.
* **Cons:** Slow startup; lower transcription accuracy.

### `**speech_recognition**`

* **Pros:** Faster, more accurate speech-to-text.
* **Cons:** Requires manual Porcupine integration and custom spinner code.

### **Conclusion:**
Although `RealtimeSTT` simplifies setup, its performance and accuracy don’t meet our needs. For this application, we’ll use `**speech_recognition**` for its superior speed and transcription quality.
