from playsound import playsound as super_playsound
import random
import os

class PlaySound:
    """
    Play a given sound file, or choose a random one from hello or bye folders.
    """

    def __init__(self, hello_folder: str = "legos/replies/hello", bye_folder: str = "legos/replies/bye"):
        self.hello_folder = hello_folder
        self.bye_folder = bye_folder

    def play(self, file_path: str = None, mode: str = None):
        """
        file_path → play that file directly.
        mode='hello' → play random from hello folder.
        mode='bye'   → play random from bye folder.
        If no file_path or mode → default to bye folder random.
        """
        def safe_path(path):
            """Return absolute, normalized path for Windows compatibility."""
            return os.path.abspath(os.path.normpath(path))

        if file_path:
            if os.path.exists(file_path):
                super_playsound(safe_path(file_path))
            else:
                print(f"[red]Audio file not found:[/] {file_path}")
            return

        # Choose folder based on mode
        if mode == "hello":
            folder = self.hello_folder
        elif mode == "bye" or mode is None:
            folder = self.bye_folder
        else:
            print(f"[red]Invalid mode:[/] {mode}")
            return

        # Play random file from the chosen folder
        if os.path.isdir(folder):
            files = [f for f in os.listdir(folder) if f.lower().endswith((".mp3", ".wav"))]
            if files:
                chosen = os.path.join(folder, random.choice(files))
                super_playsound(safe_path(chosen))
            else:
                print(f"[red]No audio files found in folder:[/] {folder}")
        else:
            print(f"[red]Folder not found:[/] {folder}")
