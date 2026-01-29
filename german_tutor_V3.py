from MODEL_3.audio import stt, wake_word,tts
from MODEL_3.LLM import correction_engine
from MODEL_3.RAG import *

import yaml
from pathlib import Path

# Load config file
CONFIG_PATH = Path("MODEL_3\config.yaml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()


# 1. wake word
# -------------
while True:
    detector = wake_word.WakeWordDetector(
                keyword = config["audio"]["wake_word"],
                sensitivity = config["audio"]["sensitivity"]
            )
    try:
        if detector.wait_for_wake_word():
            
            # 2. sst
            # -------
            my_stt = stt.FasterWhisperSTT(
                model_size = config["faster_whisper"]["model_size"],
                device = config["faster_whisper"]["device"],
                compute_type = config["faster_whisper"]["compute_type"],
                language = config["faster_whisper"]["language"],
                beam_size = config["faster_whisper"]["beam_size"],
                vad_filter = config["faster_whisper"]["vad_filter"]
            )
            
            try:                
                while True:
                    transcript = my_stt.listen_and_transcribe()
                    
                    if transcript:
                        if transcript == "__END_SESSION__":
                            print("\nSession ended")
                            break
                        
                        # 3. rag
                        # --------
                        
                        # 4. llm
                        # -------
                        model = correction_engine.GermanTutor(
                            model= config["LLM"]["model"]
                        )
                        response = model.response(
                            prompt= transcript,
                            use_simple_format= config["LLM"]["use_simple_format"]
                            )
                        
                        # 5. tts
                        # -------
                        my_tts = tts.EdgeTTS(
                                voice=config["audio"]["voice"],
                                rate = config["audio"]["rate"],
                                pitch = config["audio"]["pitch"]
                                )
                        my_tts.speak(response)
                    
            except KeyboardInterrupt:
                print("\nInterrupted by user")
            finally:
                my_stt.cleanup()
                
    finally:
        detector.cleanup()

