from MODEL_3.audio import stt, wake_word, tts
from MODEL_3.graph import tutor_graph, config
from MODEL_3.LLM.response_formatter import SimpleFormatter, ResponseFormatter
from langchain_core.messages import HumanMessage

import yaml
from pathlib import Path
from rich.console import Console
import threading

print("=================================================\n\n\n")

console = Console()
console.print("German Tutor started.", style="bold magenta")
console.print("Mode: Text" if config["toggle_text_mode"] else "Mode: Audio", style="magenta")

# Graph session config (gives the checkpointer a thread to store history in)
graph_config = {
    "configurable": {"thread_id": "main_session"}
    }

# TTS (shared across modes) 
# ----------------------------
my_tts = tts.EdgeTTS(
    voice=config["audio"]["voice"],
    rate=config["audio"]["rate"],
    pitch=config["audio"]["pitch"]
)

# Formatter
# ---------
formatter = SimpleFormatter() if config["LLM"]["use_simple_format"] else ResponseFormatter()

# Text Mode 
# -----------
if config["toggle_text_mode"]:
    while True:
        try:
            console.print("\n> You: ", style="bold cyan", end="")
            transcript = input()
            my_tts.stop()  # interrupt TTS immediately on any Enter press

            if not transcript.strip():
                continue

            # Show thinking indicator
            with formatter.console.status("[bold magenta]🤔 Thinking...[/bold magenta]", spinner="dots"):
                # call the graph
                result = tutor_graph.invoke({"messages": [HumanMessage(content=transcript)]}, 
                                            config=graph_config)
                llm_response = result["messages"][-1].content

            # Format and print
            clean_response = formatter.format_and_print(llm_response, user_input=transcript)
            
            # Speak the response (non-blocking, user can interrupt by typing)
            threading.Thread(target=my_tts.speak, args=(llm_response,), daemon=True).start()

        except KeyboardInterrupt:
            console.print("\nGoodbye!", style="bold red")
            break

# Audio Mode 
# ------------
else:
    detector = wake_word.WakeWordDetector(
        keyword=config["audio"]["wake_word"],
        sensitivity=config["audio"]["sensitivity"]
    )
    my_stt = stt.FasterWhisperSTT(
        model_size=config["faster_whisper"]["model_size"],
        device=config["faster_whisper"]["device"],
        compute_type=config["faster_whisper"]["compute_type"],
        language=config["faster_whisper"]["language"],
        beam_size=config["faster_whisper"]["beam_size"],
        vad_filter=config["faster_whisper"]["vad_filter"]
    )
    stop_event = threading.Event()

    def enter_to_stop():
        while not stop_event.is_set():
            input()
            my_tts.stop()

    enter_thread = threading.Thread(target=enter_to_stop, daemon=True)
    enter_thread.start()

    try:
        console.print("\n[dim]Say '[bold]jarvis[/bold]' to start the session... (or press [bold]Enter[/bold] to stop TTS anytime)[/dim]")
        detector.wait_for_wake_word()
        
        while True:
            transcript = my_stt.listen_and_transcribe()

            if not transcript:
                continue
            if transcript == "__END_SESSION__":
                print("\nSession ended")
                break

            my_tts.stop()  # interrupt TTS if still speaking from previous answer

            # Show thinking indicator
            with formatter.console.status("[bold magenta]🤔 Thinking...[/bold magenta]", spinner="dots"):
                # call the graph
                result = tutor_graph.invoke({"messages": [HumanMessage(content=transcript)]}, 
                                            config=graph_config)
                llm_response = result["messages"][-1].content

            # Format and print
            clean_response = formatter.format_and_print(llm_response, user_input=transcript)
            
            # Speak the response (non-blocking — wake word can interrupt)
            threading.Thread(target=my_tts.speak, args=(llm_response,), daemon=True).start()

    except KeyboardInterrupt:
        stop_event.set()
        my_tts.stop()
        print("\nInterrupted by user")
        console.print("\nGoodbye!", style="bold red")
    finally:
        stop_event.set()
        my_tts.stop()
        my_stt.cleanup()
        detector.cleanup()

