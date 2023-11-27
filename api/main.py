from fastapi import FastAPI,UploadFile,File,Form,Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
import azure.cognitiveservices.speech as speechsdk
import speech_recognition as sr
from pydantic import BaseModel
import tempfile
import gtts as gt
import uvicorn
import tempfile
import aiofiles
import pyttsx3
import pydub
import os
from dotenv import load_dotenv

load_dotenv()
AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')
WIT_AI_KEY = os.getenv('WIT_AI_KEY')
WIT_AI_KEY_SPANISH = os.getenv('WIT_AI_KEY_SPANISH')
HOUNDIFY_CLIENT_ID = os.getenv('HOUNDIFY_CLIENT_ID')
HOUNDIFY_CLIENT_KEY = os.getenv('HOUNDIFY_CLIENT_KEY')


app = FastAPI()
ffmpeg_path = "C:/Program Files/ffmpeg/bin/ffmpeg.exe"
os.environ["FFMPEG_PATH"]= ffmpeg_path
# Specify the allowed origins for CORS
origins = [
    "http://127.0.0.1:3000",  #  URL of your front-end
    "http://127.0.0.1:2000",  #  URL of your front-end
    "http://127.0.0.1:1000",  #  URL of your front-end
]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/recognize_speech")
async def upload_audio(
    audio: UploadFile = File(...),
    language: str = Form(...),
    model: str = Form(...)
):

    # Create a temporary file to store the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
        async with aiofiles.open(temp_audio_path, "wb") as temp_file:
            while chunk := await audio.read(1024):
                await temp_file.write(chunk)

        # Convert the temporary audio file to WAV
        wav_file_path = temp_audio_path + ".wav"
        convert_webm_to_wav(temp_audio_path, wav_file_path)

        # Recognize speech from the WAV file
        recognized_text = await perform_speech_recognition(wav_file_path,language, model)

        # Return the recognized text or perform additional actions
        return {"recognized_text": recognized_text}

def convert_webm_to_wav(input_file_path, output_file_path):
    # Load the webm file using pydub
    audio = pydub.AudioSegment.from_file(input_file_path, format='webm')

    # Set the sample width to 2 bytes (16-bit)
    audio = audio.set_sample_width(2)

    # Set the number of channels to mono
    audio = audio.set_channels(1)

    # Set the sample rate to 16kHz
    audio = audio.set_frame_rate(16000)

    # Export the audio as a WAV file
    audio.export(output_file_path, format='wav')

async def perform_speech_recognition(wav_file_path,language, model):
    r = sr.Recognizer()

    # Load the WAV file as audio data
    with sr.AudioFile(wav_file_path) as audio_file:
        audio = r.record(audio_file)
    print("language",language)
    print("model",model)
    recognized_text = ""

    if language == "english":
        if model == "Sphinx":
            try:
                recognized_text = r.recognize_sphinx(audio)
            except sr.UnknownValueError:
                recognized_text = "Sphinx could not understand audio"
            except sr.RequestError as e:
                recognized_text = "Sphinx error: {0}".format(e)
        elif model == "Google":
            try:
                recognized_text = r.recognize_google(audio)
            except sr.UnknownValueError:
                recognized_text = "Google Speech Recognition could not understand audio"
            except sr.RequestError as e:
                recognized_text = "Could not request results from Google Speech Recognition service: {0}".format(e)
        elif model == "Wit":
            try:
                recognized_text = r.recognize_wit(audio, key=WIT_AI_KEY)
            except sr.UnknownValueError:
                recognized_text = "Wit.ai could not understand audio"
            except sr.RequestError as e:
                recognized_text = "Could not request results from Wit.ai service: {0}".format(e)
        elif model == "Houndify":
            try:
                recognized_text = r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY)[0]
            except sr.UnknownValueError:
                recognized_text = "Houndify could not understand audio"
            except sr.RequestError as e:
                recognized_text = "Could not request results from Houndify service: {0}".format(e)
        elif model == "Whisper":
            try:
                recognized_text = r.recognize_whisper(audio, language='english')
            except sr.UnknownValueError:
                recognized_text = "Whisper could not understand audio"
            except sr.RequestError as e:
                recognized_text = "Whisper error: {0}".format(e)
        elif model == "Tensorflow":
            try:
                spoken = r.recognize_tensorflow(audio, tensor_graph='./../tf_files/conv_actions_frozen.pb', tensor_label='./../tf_files/conv_actions_labels.txt')
                recognized_text = "Tensorflow thinks you said: " + spoken
            except sr.UnknownValueError:
                recognized_text = "Tensorflow could not understand audio"
            except sr.RequestError as e:
                recognized_text = "Could not request results from Tensorflow service: {0}".format(e)
        
        elif model == "Azure":
            # Microsoft Azure Speech
            try:
                 recognized_text = str(r.recognize_azure(audio, key=AZURE_SPEECH_KEY,language='es-ES',location=AZURE_SPEECH_REGION)[0])
            except sr.UnknownValueError:
                print("Microsoft Azure Speech could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Microsoft Azure Speech service; {0}".format(e))

        else:
            recognized_text = "Invalid model selection"

    elif language == "spanish":
        if model == "Google":
            try:
                recognized_text = r.recognize_google(audio, language="es-ES")
            except sr.UnknownValueError:
                recognized_text = "Google Speech Recognition could not understand audio"
            except sr.RequestError as e:
                recognized_text = "Could not request results from Google Speech Recognition service: {0}".format(e)
        elif model == "Wit":
            try:
                recognized_text = r.recognize_wit(audio, key=WIT_AI_KEY_SPANISH)
            except sr.UnknownValueError:
                recognized_text = "Wit.ai could not understand audio"
            except sr.RequestError as e:
                recognized_text = "Could not request results from Wit.ai service: {0}".format(e)
        elif model == "Whisper":
            try:
                recognized_text = r.recognize_whisper(audio, language='spanish')
            except sr.UnknownValueError:
                recognized_text = "Whisper could not understand audio"
            except sr.RequestError as e:
                recognized_text = "Whisper error: {0}".format(e)
        elif model == "Azure":
            # Microsoft Azure Speech
            try:
                 recognized_text = str(r.recognize_azure(audio, key=AZURE_SPEECH_KEY,language='es-ES',location=AZURE_SPEECH_REGION)[0])
            except sr.UnknownValueError:
                print("Microsoft Azure Speech could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Microsoft Azure Speech service; {0}".format(e))
            
        else:
            recognized_text = "Invalid language selection"

    return {"recognized_text": recognized_text}



class TextToSpeechRequest(BaseModel):
    text: str
    language: str
    model: str
@app.post("/text-to-speech")
async def convert_text_to_speech(request: TextToSpeechRequest):
    audio_file = text_to_speech_function(request.text, request.language,request.model)
    response = Response(content=audio_file, media_type="audio/mpeg")
    response.headers["Content-Disposition"] = 'attachment; filename="audio_file.mp3"'
    return response

def text_to_speech_function(text, language,model):
    print("language",language)
    if(language == 'english'):
        language = 'en-US'
    elif(language == 'spanish'):
        language = 'es-ES'


    # Create a temporary file with .mp3 extension
    temp_file_path = tempfile.NamedTemporaryFile(suffix=".mp3", prefix="temp_audio_",delete=False).name
    
    # os.close(temp_file_handle)
    if model == 'gtts':
        t2s = gt.gTTS(text, lang=language)
        t2s.save(temp_file_path)
        # Read the contents of the temporary file

    if model == 'pytts':
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')   # getting details of current speaking rate
        engine.setProperty('rate', 125)     # setting up new voice rate
        """VOLUME"""
        volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
        engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1
        """VOICE"""
        voices = engine.getProperty('voices')    
        engine.setProperty('voice', voices[1].id)  #changing index, changes voices. o for male
        #  Save the audio to a BytesIO object
        print("temp_file.name,",temp_file_path)
        # engine.save_to_file(text,temp_file_path)  
        engine.save_to_file(text,temp_file_path)
        engine.runAndWait()
    if model == 'Azure':
        speech_key, service_region = AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

        speech_config.speech_synthesis_language = language
        if language == 'en-US':
            voice = "Microsoft Server Speech Text to Speech Voice (en-US, JennyNeural)"
        else:
            voice = 'Microsoft Server Speech Text to Speech Voice (es-ES, EliasNeural)'
        
        speech_config.speech_synthesis_voice_name = voice
        file_config = speechsdk.audio.AudioOutputConfig(filename=temp_file_path,use_default_speaker= True)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)
        result = speech_synthesizer.speak_text_async(text).get()

        # Open the temporary file and read the audio data
    with open(temp_file_path, 'rb') as file:
        audio_data = file.read()   

    # size_in_bytes = sys.getsizeof(audio_data)
    # print("size_in_bytes",size_in_bytes)

    return audio_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)