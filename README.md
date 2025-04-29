# FoodCam - Food Calorie Estimation Camera

FoodCam is a web application that allows users to upload food photos and receive a predicted food type, estimated calorie count, and nutritional breakdown.

The project uses computer vision and language models to automate calorie estimation from food images.

---

## ✨ Features

- Upload food photos via a simple web interface
- Automatic food type classification using a PyTorch ResNet18 model
- Estimation of food calorie count and nutritional components using Google's Gemini AI
- Area detection of food item vs. total image area (OpenCV contour detection)
- History system: logged-in users and guests can view their past scans
- Prevents duplicate saves on page reloads or back/forward navigation
- Admin panel for managing uploads and history
- Session support for anonymous users

---

## 🏗️ Technologies Used

- Python 3.12
- Django 5.2
- Django REST Framework
- PyTorch
- OpenCV
- Google Gemini API
- Bootstrap (planned for front-end styling)

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
