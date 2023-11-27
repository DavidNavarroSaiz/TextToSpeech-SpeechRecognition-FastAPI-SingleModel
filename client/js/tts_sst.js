//API to handle audio recording 
document.addEventListener("DOMContentLoaded", () => {
  const speakButton = document.getElementById("speakButton");
  speakButton.addEventListener("click", () => {
    const textToSpeech = document.getElementById("textToSpeech").value;
    const languageSelect = document.getElementById("language-select");
    const model_tts = document.getElementById("modelSelect_tts").value;

    const selectedLanguage = languageSelect.value;
    fetch("http://localhost:8000/text-to-speech", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: textToSpeech, language: selectedLanguage,model:model_tts })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Request failed with status " + response.status);
      }
      return response.blob();
    })
    .then(audioBlob => {
      const audioUrl = URL.createObjectURL(audioBlob);
      const audioElement = document.createElement("audio");
      audioElement.src = audioUrl;
      audioElement.controls = true;
      document.body.appendChild(audioElement);
      audioElement.play();
    })
    .catch(error => {
      console.error("Error:", error);
    });
  });
});
var audioRecorder = {
    /** Stores the recorded audio as Blob objects of audio data as the recording continues*/
    audioBlobs: [],/*of type Blob[]*/
    /** Stores the reference of the MediaRecorder instance that handles the MediaStream when recording starts*/
    mediaRecorder: null, /*of type MediaRecorder*/
    /** Stores the reference to the stream currently capturing the audio*/
    streamBeingCaptured: null, /*of type MediaStream*/
    /** Start recording the audio 
     * @returns {Promise} - returns a promise that resolves if audio recording successfully started
     */
    start: function () {
        //Feature Detection
        if (!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)) {
            //Feature is not supported in browser
            //return a custom error
            return Promise.reject(new Error('mediaDevices API or getUserMedia method is not supported in this browser.'));
        }

        else {
            //Feature is supported in browser

            //create an audio stream
            return navigator.mediaDevices.getUserMedia({ audio: true }/*of type MediaStreamConstraints*/)
                //returns a promise that resolves to the audio stream
                .then(stream /*of type MediaStream*/ => {

                    //save the reference of the stream to be able to stop it when necessary
                    audioRecorder.streamBeingCaptured = stream;

                    //create a media recorder instance by passing that stream into the MediaRecorder constructor
                    audioRecorder.mediaRecorder = new MediaRecorder(stream); /*the MediaRecorder interface of the MediaStream Recording
                    API provides functionality to easily record media*/

                    //clear previously saved audio Blobs, if any
                    audioRecorder.audioBlobs = [];

                    //add a dataavailable event listener in order to store the audio data Blobs when recording
                    audioRecorder.mediaRecorder.addEventListener("dataavailable", event => {
                        //store audio Blob object
                        audioRecorder.audioBlobs.push(event.data);
                    });

                    //start the recording by calling the start method on the media recorder
                    audioRecorder.mediaRecorder.start();
                });

            /* errors are not handled in the API because if its handled and the promise is chained, the .then after the catch will be executed*/
        }
    },
    /** Stop the started audio recording
     * @returns {Promise} - returns a promise that resolves to the audio as a blob file
     */
    stop: function () {
        // Save a reference to the audioRecorder object
        const recorder = audioRecorder;
        // Get the selected language
        const languageSelect = document.getElementById('language-select');
        const selectedLanguage = languageSelect.value;

        // Get the selected model
        const modelSelect = document.getElementById('model-select');
        const selectedModel = modelSelect.value;
        // Create a promise to return the audio blob
        const promise = new Promise(resolve => {
          // Save audio type to pass to set the Blob type
          const mimeType = recorder.mediaRecorder.mimeType;
      
          // Listen to the stop event in order to create & return a single Blob object
          recorder.mediaRecorder.addEventListener("stop", () => {
            // Create a single blob object, as we might have gathered a few Blob objects that need to be joined as one
            const audioBlob = new Blob(recorder.audioBlobs, { type: mimeType });
      
            // Resolve the promise with the single audio blob representing the recorded audio
            resolve(audioBlob);
          });
      
          // Cancel the audio recording
          recorder.cancel();
        });
      
        // Make an HTTP request to the API endpoint separately
        promise.then(audioBlob => {
          if (audioBlob) {
            // Create a FormData object to send the audio file
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav'); // Modify the filename as needed
            formData.append('language', selectedLanguage);
            formData.append('model', selectedModel);
            // Make the API request
            fetch('http://127.0.0.1:8000/recognize_speech', {
              method: 'POST',
              body: formData
            })
              .then(response => response.json())
              .then(data => {
                // Handle the API response as needed
                // console.log(data);
                console.log(data.recognized_text);
                // Display the result in the textarea
                if (data && data.recognized_text && data.recognized_text.recognized_text) {
                  // Display the result in the textarea
                  const resultTextarea = document.querySelector('.result-textarea');
                  resultTextarea.value = data.recognized_text.recognized_text;
                } else {
                  console.error('Invalid API response:', data);
                }
                
              })
              .catch(error => {
                // Handle any errors that occur during the API request
                console.error('Error:', error);
              });
          }
        });
      
        // Return the original promise without modification
        return promise;
      },
    /** Cancel audio recording*/
    cancel: function () {
        //stop the recording feature
        audioRecorder.mediaRecorder.stop();

        //stop all the tracks on the active stream in order to stop the stream
        audioRecorder.stopStream();

        //reset API properties for next recording
        audioRecorder.resetRecordingProperties();
    },
    /** Stop all the tracks on the active stream in order to stop the stream and remove
     * the red flashing dot showing in the tab
     */
    stopStream: function () {
        //stopping the capturing request by stopping all the tracks on the active stream
        audioRecorder.streamBeingCaptured.getTracks() //get all tracks from the stream
            .forEach(track /*of type MediaStreamTrack*/ => track.stop()); //stop each one
    },
    /** Reset all the recording properties including the media recorder and stream being captured*/
    resetRecordingProperties: function () {
        audioRecorder.mediaRecorder = null;
        audioRecorder.streamBeingCaptured = null;

        /*No need to remove event listeners attached to mediaRecorder as
        If a DOM element which is removed is reference-free (no references pointing to it), the element itself is picked
        up by the garbage collector as well as any event handlers/listeners associated with it.
        getEventListeners(audioRecorder.mediaRecorder) will return an empty array of events.*/
    }
}



