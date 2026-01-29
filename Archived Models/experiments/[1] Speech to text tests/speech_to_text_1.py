from RealtimeSTT import AudioToTextRecorder
from termcolor import colored


# callback functions (recommended)
def process_text(text):
    print(text)

def my_start_callback():
    print("\n✅ Recording started!")

def my_stop_callback():
    print("\n❌ Recording stopped!")
    
    
# 1. auto mode runs an infite loop
def auto_mode(recorder, jarvis = False):
    
    while True:
        if jarvis:
            print(colored('\n\n> Awaiting wake word "Jarvis"...', 'blue'))
            
        recorder.text(process_text)

# 2. press enter to stop recordering
def push_to_stop_mode(recorder):
    recorder.start()
    input("Press Enter to stop recording...")
    recorder.stop()
    print("Transcription: ", recorder.text())

# ======================================================================== #
# ===========================  MAIN   ==================================== #
# ======================================================================== #


if __name__ == '__main__':

    # testing german [PASSED ✅]
    recorder = AudioToTextRecorder(
        wakeword_backend="pvporcupine",
        wake_words="jarvis",                 # if using wake word
        language="de",                       # restrict transcription to German
        wake_words_sensitivity=0.8
    )
    
    auto_mode(recorder, jarvis = True)

# ======================================================================== #

    # # testing callbacks controll [PASSED ✅]
    # print("Wait until it says 'speak now'")
    # recorder = AudioToTextRecorder(on_recording_start=my_start_callback,
    #                             on_recording_stop=my_stop_callback)
    # auto_mode(recorder)
    
# ======================================================================== #

    # # testing wakeup words [PASSED ✅]
    # recorder = AudioToTextRecorder(
    #                             wakeword_backend="pvporcupine",
    #                             wake_words="jarvis",
    #                             wake_words_sensitivity=0.5
    #                         )

    
    # print('Say "Jarvis" to start recording...')
    # auto_mode(recorder)

# ======================================================================== #

    # # testing both modes [PASSED ✅]
    # print("Wait until it says 'speak now'")
    # recorder = AudioToTextRecorder()
    
    # while (1):
    #     print ("press: 1 for auto mode")
    #     print ("press: 2 for push to stop mode")
    #     mode = int(input("mode: "))
        
    #     if (mode == 1):
    #         auto_mode(recorder)
    #         continue
    #     elif (mode == 2):
    #         push_to_stop_mode(recorder)
    #         continue