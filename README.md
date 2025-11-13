# 🩺 AI Healthcare Assistant

A production-ready multi-agent AI healthcare assistant built with LangGraph, LangChain, Groq LLM, and Tavily API.

## ✨ Features

- **5 Intelligent Agents** working in collaboration:
  - 🧠 Symptom Analyzer - Analyzes symptoms and identifies possible conditions
  - 💊 Medication Agent - Suggests medications with safety information
  - 🌿 Home Remedies Agent - Provides natural treatment options
  - 🥗 Diet & Lifestyle Advisor - Offers nutritional and lifestyle guidance
  - 👨‍⚕️ Doctor Recommendation Agent - Suggests relevant specialists

- **Real-time Verified Data** via Tavily API
- **Modern Streamlit UI** with collapsible cards and responsive design
- **LangGraph Workflow** for seamless agent coordination
- **Comprehensive Error Handling** and safety disclaimers

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

**Get your API keys:**
- Groq API: https://console.groq.com/
- Tavily API: https://tavily.com/

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📋 Requirements

- Python 3.8+
- Groq API key
- Tavily API key

## 🏗️ Project Structure

The project is organized into modular components:

```
HealthCare Chatbot/
├── app.py              # Main entry point - orchestrates UI and agents
├── agents.py           # All agent definitions and LangGraph workflow
├── ui.py               # Streamlit UI components and styling
├── config.py           # API client initialization and configuration
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## 📐 Architecture

```
User Input (UI)
    ↓
app.py (Main Orchestrator)
    ↓
agents.py (LangGraph Workflow)
    ├── Symptom Analyzer Agent
    ├── Medication Agent
    ├── Home Remedies Agent
    ├── Diet & Lifestyle Advisor Agent
    └── Doctor Recommendation Agent
    ↓
Results Display (UI)
```

### Component Responsibilities

- **`app.py`**: Main entry point that initializes clients, manages session state, and coordinates between UI and agents
- **`agents.py`**: Contains all 5 agent functions, state definition, Tavily search helper, and LangGraph workflow creation
- **`ui.py`**: All Streamlit UI components including header, sidebar, input forms, results display, and styling
- **`config.py`**: Handles environment variable loading and API client initialization (Groq LLM and Tavily)

## ⚠️ Important Disclaimer

This AI Healthcare Assistant is designed for **informational and educational purposes only**. It does not provide medical diagnosis, treatment, or professional medical advice. Always consult with a qualified healthcare provider for any health concerns or before making any medical decisions.

## 🛠️ Technology Stack

- **LangGraph** - Multi-agent workflow coordination
- **LangChain** - LLM orchestration
- **Groq LLM (Llama-3-70b)** - Reasoning and responses
- **Tavily API** - Real-time health data retrieval
- **Streamlit** - Interactive frontend

## 📝 License

This project is for educational purposes.

