document.addEventListener('DOMContentLoaded', function () {
    const welcomeScreen = document.getElementById('welcome-screen');
    const welcomeCaption = document.getElementById('welcome-caption');
    const mainInterface = document.getElementById('main-interface');

    // Wrap each letter of the caption in span tags for animation
    welcomeCaption.innerHTML = welcomeCaption.textContent.split("").map(letter => `<span>${letter}</span>`).join("");

    // Show the main interface after the caption finishes fading out
    welcomeScreen.addEventListener('click', function () {
        const letterSpans = document.querySelectorAll('.fade-caption span');
        
        // Faster letter fade-out (reduce duration)
        letterSpans.forEach((span, index) => {
            span.style.animation = `fadeOutLetter 0.3s ease-in-out forwards`; // Faster fade-out
            span.style.animationDelay = `${index * 0.05}s`; // Shorter delay between each letter
        });

        // Wait for the last letter to finish animating before switching screens
        setTimeout(() => {
            welcomeScreen.classList.add('hidden');
            mainInterface.classList.remove('hidden');
        }, letterSpans.length * 50 + 500); // Adjust timing based on faster fade-out
    });

    const captureButton = document.getElementById('capture-button');
    const backendButton = document.getElementById('view-backend');
    const emotionResult = document.getElementById('emotion-result');
    const selectedImage = document.getElementById('selected-image');
    const videoContainer = document.getElementById('video-container');
    const videoStreamElement = document.getElementById('camera-stream');

    let isCameraOpen = false;
    let videoStream = null;

    function resetUI() {
        // Hide captured image and reset UI
        selectedImage.classList.add('hidden');
        videoContainer.classList.add('hidden');
        emotionResult.innerText = 'None';
        selectedImage.src = '';
    }

    captureButton.addEventListener('click', function () {
        if (!isCameraOpen) {
            resetUI();
    
            // Open the user's camera
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function (stream) {
                    videoStream = stream;
                    videoStreamElement.srcObject = stream;
                    videoContainer.classList.remove('hidden');
                    captureButton.innerText = 'Take a Snapshot';
                    isCameraOpen = true;
                })
                .catch(function (error) {
                    alert("Unable to access camera. Please allow camera permissions.");
                });
        } else {
            // Take a snapshot
            const canvas = document.createElement('canvas');
            canvas.width = videoStreamElement.videoWidth;
            canvas.height = videoStreamElement.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(videoStreamElement, 0, 0, canvas.width, canvas.height);
    
            // Convert the canvas image to a blob
            canvas.toBlob(function (blob) {
                const formData = new FormData();
                formData.append('image', blob, 'snapshot.jpg'); // Append the image as 'snapshot.jpg'
    
                // Send the image to the backend for processing
                fetch('/upload_image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    // Update the UI with the predicted emotion
                    emotionResult.innerText = data.predicted_emotion;
                    selectedImage.src = URL.createObjectURL(blob);  // Show the snapshot image
                    selectedImage.classList.remove('hidden');
                    videoContainer.classList.add('hidden');
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error processing the image.');
                });
            }, 'image/jpeg');
    
            // Stop the video stream
            videoStream.getTracks().forEach(track => track.stop());
    
            captureButton.innerText = 'Capture Emotion';
            isCameraOpen = false;
        }
    });

    
});
