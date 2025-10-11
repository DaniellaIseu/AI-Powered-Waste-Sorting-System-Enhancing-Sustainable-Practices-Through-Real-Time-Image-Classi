[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/inoLPW_E)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20151161&assignment_repo_type=AssignmentRepo)



♻️ AI-Powered Waste Sorting System
🎯 Project Overview
An intelligent waste classification system that uses Computer Vision and Deep Learning to automatically sort waste materials in real-time. Designed specifically for small shops and local markets in Kenya, promoting sustainable waste management practices through AI-powered automation and educational feedback.

✨ Key Features
🤖 AI-Powered Classification: Real-time waste detection using Convolutional Neural Networks (CNN)

📱 Mobile-First Design: Accessible via web browser on any smartphone

🌍 Kenyan Context: Trained on local waste types and market environments

♻️ Eco-Feedback: Instant recycling instructions and environmental education

📊 User Analytics: Track recycling habits and environmental impact

🔒 User Authentication: Secure login and personalized dashboard

🛠️ Technology Stack
Backend & AI
Python 3.8+ - Core programming language

TensorFlow/Keras - Deep learning framework

Flask - Web application framework

OpenCV - Image processing

MobileNetV2 - Lightweight CNN architecture

Frontend
HTML5/CSS3 - Responsive web interface

JavaScript - Interactive features

Bootstrap - Mobile-first design

Data & Deployment
TrashNet Dataset - Base training data

Custom Kenyan Dataset - Local waste images

TensorFlow Lite - Optimized for mobile deployment

🚀 Quick Start
Prerequisites
bash
Python 3.8+
TensorFlow 2.0+
Flask
Pillow
NumPy
Installation & Running
Clone the repository

bash
git clone https://github.com/DaniellaIseu/AI-Powered-Waste-Sorting-System.git
cd AI-Powered-Waste-Sorting-System
Install dependencies

bash
pip install -r requirements.txt
Run the application

bash
cd web_app
python app.py
Access the application

Local: http://localhost:5000

Network: http://[YOUR-IP]:5000 (for mobile testing)

📁 Project Structure
text
AI-Powered-Waste-Sorting-System/
├── ai_model/                 # AI Training & Model Development
│   ├── train.py             # Model training script
│   ├── waste_classifier.h5  # Trained model
│   └── data/                # Training datasets
├── web_app/                 # Web Application
│   ├── app.py              # Flask application
│   ├── templates/          # HTML templates
│   ├── static/             # CSS/JS assets
│   └── uploads/            # User uploads directory
└── documentation/          # Project documentation
🎓 Research Objectives
Identify common waste types in Kenyan small shops and markets

Train a lightweight image classification model for real-time detection

Implement an offline-capable system for low-infrastructure environments

Incorporate educational feedback mechanisms for behavior change

Evaluate system usability, accuracy, and behavioral impact

🌱 Environmental Impact
This project supports UN Sustainable Development Goal 12 (Responsible Consumption and Production) by:

♻️ Increasing recycling rates through automated sorting

📚 Educating users about proper waste disposal

🌍 Reducing environmental pollution in urban areas

💡 Promoting sustainable practices in informal economies

🔬 Technical Implementation
Model Architecture
Base Model: MobileNetV2 (pre-trained on ImageNet)

Transfer Learning: Fine-tuned on waste classification task

Optimization: TensorFlow Lite for mobile deployment

Accuracy: >85% validation accuracy on combined datasets

Data Pipeline
Data Collection: TrashNet + Custom Kenyan waste images

Preprocessing: Image augmentation, normalization, resizing

Training: Transfer learning with aggressive data augmentation

Validation: 80-20 split with cross-validation

📊 Performance Metrics
Classification Accuracy: 85%+

Inference Time: <3 seconds

Model Size: <10MB (optimized for mobile)

Offline Capability: Full functionality without internet

👥 Target Users
Small Shop Owners in urban and peri-urban areas

Local Market Vendors in informal settlements

Waste Management Companies for sorting facilities

Environmental NGOs for awareness campaigns

🎯 Future Enhancements
Mobile app development (Flutter/React Native)

Multi-language support (Swahili, Local dialects)

Gamification features for user engagement

Integration with recycling collection services

Real-time camera processing on mobile devices

🙏 Acknowledgments
Strathmore University - Academic supervision and support

TrashNet Dataset - Base training data

Google TensorFlow Team - Open-source AI tools

UN Environment Programme - Waste management research


GitHub: @DaniellaIseu

Project Link: https://github.com/DaniellaIseu/AI-Powered-Waste-Sorting-System
