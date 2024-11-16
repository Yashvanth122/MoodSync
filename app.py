from flask import Flask, render_template, request, jsonify
import numpy as np
from PIL import Image
import io
import tensorflow as tf
import requests

app = Flask(__name__)

# Load the CNN model
model = tf.keras.models.load_model('best_model.keras')

# Preprocess image function
def preprocess_image(image):
    try:
        img = image.resize((64, 64))  # Resize the image to 64x64 (as expected by the model)
        img_array = np.array(img)  # Convert to numpy array
        print(f"Image converted to array: {img_array.shape}")  # Check the shape of the array
        img_array = img_array / 255.0  # Normalize the image
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        return img_array
    except Exception as e:
        print(f"Error during image preprocessing: {e}")
        raise

# Brightness levels for each emotion
EMOTION_BRIGHTNESS = {
    'Happy': 90,
    'Sad': 20,
    'Neutral': 50
    # Add more mappings if you have additional emotions
}

# Philips Hue API configuration
HUE_BRIDGE_IP = '192.168.2.159'  # Replace with your Philips Hue bridge IP
LIGHT_ID = '1'  # Your light ID in the bridge
API_KEY = '0uwbM4jTAojbncWxyrQZJxiBtDKvlx23GuSjZhQ1'  # Your Philips Hue API key

def set_brightness(brightness):
    url = f"http://{HUE_BRIDGE_IP}/api/{API_KEY}/lights/{LIGHT_ID}/state"
    payload = {"bri": int((brightness / 100) * 254), "on": True}  # Convert percentage to Hue brightness scale (0-254)
    try:
        print(f"Setting brightness to {brightness}%...")
        response = requests.put(url, json=payload)
        print(f"Sending brightness adjustment request to {url} with payload {payload}")
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")
        if response.status_code == 200:
            print(f"Brightness successfully set to {brightness}%")
            return True
        else:
            print("Failed to adjust brightness.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error adjusting light brightness: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        # Check if image is present in the request
        if 'image' not in request.files:
            print("No image provided")
            return jsonify({'error': 'No image provided'}), 400
        
        # Read the image from the request
        file = request.files['image']
        img = Image.open(io.BytesIO(file.read()))
        print(f"Image received and loaded with size: {img.size}")

        # Preprocess the image for the CNN model
        img_array = preprocess_image(img)
        print(f"Preprocessed image shape: {img_array.shape}")

        # Get prediction from the model
        predictions = model.predict(img_array)
        print(f"Model predictions: {predictions}")
        
        predicted_class = np.argmax(predictions, axis=1)
        print(f"Predicted class index: {predicted_class}")

        # Map the class to emotion labels
        emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        predicted_emotion = emotion_labels[predicted_class[0]]
        print(f"Predicted emotion: {predicted_emotion}")

        # Get brightness for emotion
        brightness = EMOTION_BRIGHTNESS.get(predicted_emotion, 50)  # Default to 50% if emotion not found
        print(f"Your emotion was predicted as '{predicted_emotion}'. Adjusting Philips Hue light to {brightness}% brightness.")

        # Set the brightness through Philips Hue API
        if set_brightness(brightness):
            print(f"Philips Hue light adjusted to match '{predicted_emotion}' emotion with {brightness}% brightness.")
            return jsonify({'predicted_emotion': predicted_emotion, 'brightness': brightness})
        else:
            print("Failed to adjust Philips Hue light brightness.")
            return jsonify({'predicted_emotion': predicted_emotion, 'error': 'Failed to adjust light brightness'}), 500
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({'error': f"Error processing image: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
