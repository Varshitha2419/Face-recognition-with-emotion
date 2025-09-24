# Face-recognition-with-emotion
A Python project using OpenCV and LBPH to recognize faces and detect emotions in real-time.
. Clone the Repository
git clone https://github.com/your-username/face-recognition-emotion.git
cd face-recognition-emotion

2. Create a Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

3. Install Dependencies
Make sure you have Python 3.8+ installed. Then install the requirements:
pip install -r requirements.txt
(If you don’t have a requirements.txt, I can generate one from your code.)

4. Prepare Models & Data
Ensure your LBPH face recognition model and emotion detection model are available in the models/ folder.
If you don’t have pre-trained models, first run the training scripts (if included).

5. Run the Application
For Desktop testing:
python main.py
For Backend service (Android integration):
python android_recognition.py

6. Using with Android
The Android app captures an image/frame and sends it to android_recognition.py via API.
The backend responds with:
{
  "face_id": "User_01",
  "emotion": "Happy",
  "confidence": 92.5
}

7. Project Workflow
face_crop.py → Detects and crops faces.
emotion.py → Predicts the emotion.
android_recognition.py → Exposes APIs for Android.
main.py → Ties everything together.
