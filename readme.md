### TextToSpeech-SpeechRecognition-FastAPI-Single-Model

Similar to the *FAST API all models* demo, this version allows the client to choose a specific model for speech recognition or text-to-speech conversion.


This section includes a client-server application pair using FAST API, Python, HTML, and JavaScript. The client and server components work together to offer speech recognition and text-to-speech functionality. Various models are supported for speech recognition and text-to-speech conversion.

the key difference of this project and the project[TextToSpeech-SpeechRecognition-FastAPI
](https://github.com/DavidNavarroSaiz/TextToSpeech-SpeechRecognition-FastAPI)is that it works with all the models separated, so depending on the language and model selected on the web app- client side server, the API returns the result of the single model.

*Speech Recognition models*
english:  'Google','Houndify','Whisper','Sphinx', 'Wit','Azure'
spanish: 'Google', 'Wit','Whisper','Azure'

*Text to Speech models*
english:  'gtts','pytts','Azure'
spanish: 'gtts','Azure'


## How to run 


### API:
go to the 'fast_api_speech_single_model/api'

Create a new environment
```
    python3.8 -m venv <env_name>
```
if you are using anaconda you just can write the following code line:

```
    conda create --name <env_name> python=3.8
```
activate the envitonrment:

```
    cd <env_name> \Scripts\activate.bat
```

<p>Anaconda:<p>

```
    conda activate <env_name>
```
```    
    conda install pip
    pip install -r requirements.txt
```
Setup the .env file: 
create a new .env file and paste the following commands:

```
AZURE_SPEECH_KEY = ""
AZURE_SPEECH_REGION = ""
WIT_AI_KEY = ""
WIT_AI_KEY_SPANISH = "" 
HOUNDIFY_CLIENT_ID = "" 
HOUNDIFY_CLIENT_KEY = "" 

```
for each of the keys look for the documentation about how to create an API KEY in the links:

- [Azure](Azure.com)
- [Wit](wit.com)
- [Houndify](Houndify.com)


run in the terminal:
```
uvicorn main:app --reload

```
the app now is running at:

`http://127.0.0.1:8000`

to learn what are the endpoints and how to interact with the app open the following link at the explorer:

`http://127.0.0.1:8000/docs`


### Client 

to run the client as a web server use the http server of python or any similar , to do that write in the terminal

`python -m http.server 2000`
the port(2000) has to be in the main.py in the origins section:
```
origins = [
    "http://127.0.0.1:3000",  #  URL of your front-end
    "http://127.0.0.1:2000",  #  URL of your front-end
    "http://127.0.0.1:1000",  #  URL of your front-end
]

```

you have to be in the same folder as the ./client/index.html file to run that command






## What you will find:

in the `./client/js/tts_sst.js` you can find the petitions that are done to the API
the other files are the structures and animations/buttons and functionality of the web app.



