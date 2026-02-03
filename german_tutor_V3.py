from MODEL_3.audio import stt, wake_word,tts
from MODEL_3.LLM import correction_engine
from MODEL_3.RAG import tavily_rag

import yaml
from pathlib import Path
from rich.console import Console

# Load config file
CONFIG_PATH = Path("MODEL_3\config.yaml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

console = Console()
if config["RAG"]["use_RAG"]:
    console.print("RAG is enabled.", style="bold magenta")
    console.print("Using live web search to improve answer accuracy.", style="magenta")
else:
    console.print("RAG is currently disabled.", style="bold orange3")
    console.print(
        "Enable it by setting `RAG.use_RAG: true` in the config file.",
        style="dim")

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
                        if config["RAG"]["use_RAG"]:
                            rag_response = tavily_rag.search_web(query=transcript,
                                                        include_answer=config["RAG"]["include_answer"],
                                                        search_depth=config["RAG"]["search_depth"],
                                                        max_results=config["RAG"]["max_results"])
                        
                        # 4. llm
                        # -------
                        model = correction_engine.GermanTutor(
                            model= config["LLM"]["model"]
                        )
                        llm_response = model.response(
                            prompt= transcript,
                            RAG_answer=rag_response["answer"] if config["RAG"]["use_RAG"] else None, # -> send the answer only
                            use_simple_format= config["LLM"]["use_simple_format"]
                            )
                        
                        # 5. tts
                        # -------
                        my_tts = tts.EdgeTTS(
                                voice=config["audio"]["voice"],
                                rate = config["audio"]["rate"],
                                pitch = config["audio"]["pitch"]
                                )
                        my_tts.speak(llm_response)
                    
            except KeyboardInterrupt:
                print("\nInterrupted by user")
            finally:
                my_stt.cleanup()
                
    finally:
        detector.cleanup()

