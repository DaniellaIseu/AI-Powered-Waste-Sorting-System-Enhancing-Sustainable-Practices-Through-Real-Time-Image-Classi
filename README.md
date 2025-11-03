[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/inoLPW_E)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20151161&assignment_repo_type=AssignmentRepo)



# 🌍 Smart Waste Classifier

## 📘 Overview
The **Smart Waste Classifier** is an AI-powered application that automatically classifies waste materials (plastic, metal, paper, glass, organic, etc.) using computer vision.  
It consists of:
- A **Web App** for uploading and classifying waste images.
- A **Mobile App** (Jetpack Compose) for real-time image capture and classification.
- An **Admin Dashboard** for monitoring system statistics and user performance.

---

## 🎯 Objectives
- Train a CNN-based image classification model for waste recognition.
- Enable real-time camera-based waste detection in the mobile app.
- Provide an admin dashboard to visualize classification metrics.
- Promote environmental sustainability through technology.

---

## 🧠 AI Model
- **Base Model:** MobileNetV2 (transfer learning)
- **Framework:** TensorFlow / Keras
- **Accuracy Achieved:** 75.55% (fine-tuning phase ongoing)
- **Classes:** Plastic, Paper, Metal, Organic, Glass, Trash

---

## 🖥️ Web App Features
- Upload waste images for classification.
- Display top prediction and confidence level.
- Admin dashboard showing classification metrics.
- Built using **Flask + TensorFlow + HTML/CSS/JS**.

---

## 📱 Mobile App Features
- Built with **Jetpack Compose** (Android).
- Integrates **CameraX** for image capture.
- Displays classification results on screen.
- Includes navigation bar and admin interface.

---

## ⚙️ Tech Stack
| Layer | Technology |
|-------|-------------|
| **Frontend** | Jetpack Compose (Mobile), HTML/CSS (Web) |
| **Backend** | Flask (Python) |
| **ML Model** | TensorFlow / Keras |
| **Database** | Firebase / SQLite |
| **Deployment** | Azure / Localhost |
| **Version Control** | Git & GitHub |

---

## 🧩 Installation & Setup
### 🔹 Web App
1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/waste-classifier.git
   cd waste-classifier/web
2. Install dependencies:

pip install -r requirements.txt


3. Run server:

python app.py

🔹 Mobile App

Open the mobile/ folder in Android Studio.

Build the project and run on an emulator or device.

Ensure the ML model is exported as .tflite and integrated into assets/.

📈 Future Improvements

Increase model accuracy to 90%+ through fine-tuning and dataset expansion.

Implement real-time video classification.

Add cloud synchronization for user data.

Enable notifications for sustainable waste management tips.

👩‍💻 Contributors

Daniella Iseu – Project Lead, ML Model & App Development
