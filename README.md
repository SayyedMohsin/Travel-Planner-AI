# 🌍 Agentic AI-Based Travel Planning Assistant (Voyager AI)

![Project Status](https://img.shields.io/badge/Status-Active-success)
![AI Model](https://img.shields.io/badge/AI-Llama%203.3%20%2F%20Groq-blue)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Three.js-violet)
![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20LangChain-green)

An advanced **Agentic AI System** that acts as a professional Travel Architect. Unlike basic chatbots, this system uses **Tool Calling** reasoning capabilities to fetch real-time weather, calculate budgets, generate dynamic flight/hotel options, and visualize the journey on a **Futuristic 3D Holographic Dashboard**.

---

## ✨ Key Features

### 🧠 Intelligent Agentic Core
- **Powered by Llama 3 (via Groq):** Utilizes the latest LLM for high-speed reasoning and structured JSON outputs.
- **Multi-Step Reasoning:** The agent decides which tools to call (Flight Search, Hotel Finder, Weather API) based on user input.
- **Indian Context Aware:** Specialized in planning detailed itineraries for Indian cities with cultural nuances.

### 💻 Sci-Fi 3D Interface
- **Holographic Earth:** Interactive 3D globe built with **Three.js (React Three Fiber)**.
- **Immersive Visuals:** Floating 3D elements, moving flight animations, and a curved CRT-monitor aesthetic.
- **Glassmorphism UI:** Modern, translucent UI components built with CSS-in-JS.

### 🛠️ Utility Features
- **📥 PDF Export:** Generate and download a professional trip itinerary PDF with a single click.
- **🗣️ AI Voice Assistant:** Reads out the plan in an Indian accent using the browser's Speech Synthesis API.
- **🌤️ Real-Time Weather:** Integrates with Open-Meteo API for accurate forecasts.
- **💰 Smart Budgeting:** Calculates estimated costs for flights, hotels, and daily expenses.

---

## 🏗️ Tech Stack

### **Backend (Python)**
- **Framework:** FastAPI (High-performance API)
- **AI Orchestration:** LangChain (Tool Calling Agent)
- **LLM Engine:** Groq API (Llama-3.1-8b-instant / Llama-3.3-70b)
- **Data Validation:** Pydantic
- **Server:** Uvicorn

### **Frontend (JavaScript)**
- **Library:** React.js (Vite)
- **3D Graphics:** Three.js, React Three Fiber, Drei
- **Animations:** Framer Motion
- **PDF Generation:** jsPDF
- **HTTP Client:** Axios

---

## 🚀 Installation & Setup

Follow these steps to run the project locally.

### 1️⃣ Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/Travel-Planner-AI.git](https://github.com/YOUR_USERNAME/Travel-Planner-AI.git)
cd Travel-Planner-AI

2️⃣ Backend Setup
Navigate to the backend folder and set up the Python environment.
cd backend
# Create Virtual Environment
python -m venv venv
# Activate Environment (Windows)
venv\Scripts\activate
# Activate Environment (Mac/Linux)
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

Configure API Keys: Create a .env file in the backend folder and add your Groq API Key:
GROQ_API_KEY=gsk_your_secret_key_here

Run Server:
# Runs on 0.0.0.0 to avoid CORS issues
python api.py

3️⃣ Frontend Setup
Open a new terminal and navigate to the frontend folder.
cd frontend-3d
# Install Node Modules
npm install

# Run Development Server
npm run dev

Frontend will start at: http://localhost:5173

📂 Project Structure
Travel-Planner-AI/
├── backend/                 # FastAPI & LangChain Logic
│   ├── agent/               # Agent definition & Prompt Engineering
│   ├── tools/               # Custom Tools (Flight, Hotel, Weather)
│   ├── api.py               # Main Server Entry Point
│   └── requirements.txt     # Python Dependencies
│
├── frontend-3d/             # React & Three.js App
│   ├── src/
│   │   ├── App.jsx          # Main UI & 3D Logic
│   │   └── main.jsx         # Entry point
│   ├── public/              # Assets
│   └── package.json         # JS Dependencies
│
└── README.md                # Project Documentation


📸 Screenshots
(Add screenshots of your 3D Dashboard here)



🤝 Contributing
Contributions are welcome! Please fork this repository and submit a pull request for any features or bug fixes.

📜 License
This project is licensed under the MIT License.


