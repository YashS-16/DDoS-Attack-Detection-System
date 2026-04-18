# 🛡️ DDoS Shield – Real-Time Detection System

## 📌 Overview

This project detects and analyzes potential DDoS attacks in real-time using:

* Machine Learning models (RF, XGBoost, Logistic Regression)
* Autoencoder-based anomaly detection
* Live packet capture using Scapy
* Interactive dashboard (Flask + JS)

---

## ⚙️ Features

* Live traffic monitoring
* Risk scoring system
* Attack type classification
* Real-time dashboard
* Alert system (browser notifications)
* Precaution suggestions

---

## 🚀 How to Run

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Run Backend Server

```bash
cd Backend
python app.py
```

---

### 3️⃣ Open Dashboard

Go to:

```
http://localhost:5000
```

---

### 4️⃣ Start Detection

Click **Start Monitoring** on homepage

---

## ⚠️ Important Notes

* Run terminal as **Administrator** (required for packet capture)
* Works best on **local network**
* Do NOT run attack simulations on public networks

---
