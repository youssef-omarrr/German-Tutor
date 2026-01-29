from MODEL_3.audio import stt, wake_word,tts
from MODEL_3.LLM import correction_engine
from MODEL_3.RAG import *

import yaml
from pathlib import Path

CONFIG_PATH = Path("MODEL_3\config.yaml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()



# 1. wake word
# -------------
detector = wake_word.WakeWordDetector(
                keyword = config["audio"]["wake_word"],
                sensitivity = config["audio"]["sensitivity"]
            )
try:
    while True:
        if detector.wait_for_wake_word():
            
            # 2. sst
            # -------
            my_srt = srt.FasterWhisperSTT(
                model_size = config["faster_whisper"]["model_size"],
                device = config["faster_whisper"]["device"],
                compute_type = config["faster_whisper"]["compute_type"],
                language = config["faster_whisper"]["language"],
                beam_size = config["faster_whisper"]["beam_size"],
                vad_filter = config["faster_whisper"]["vad_filter"]
            )
            
            try:                
                while True:
                    transcript = my_srt.listen_and_transcribe()
                    
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
                            transcript,
                            model= config["LLM"]["use_simple_format"]
                            )
                        
                        # 5. tts
                        # -------
                        my_tts = tts.EdgeTTS(
                                voice=config["audio"]["voice"],
                                rate = config["audio"]["rate"],
                                pitch = config["audio"]["pitch"])
                        tts.speak(response)
                        
                    else:
                        print("\n✗ No speech detected")
                    
            except KeyboardInterrupt:
                print("\nInterrupted by user")
            finally:
                my_stt.cleanup()
finally:
    detector.cleanup()

