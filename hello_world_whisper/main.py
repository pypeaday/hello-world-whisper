import whisper
from whisper.utils import get_writer

if __name__ == "__main__":
    song = "./data/01 - Silent Night.mp3"

    print("loading model")
    model = whisper.load_model("small")
    print("transcribing")
    result = model.transcribe(song)
    print("writing vtt")
    writer = get_writer("vtt", "./data")

    writer(result, song)
