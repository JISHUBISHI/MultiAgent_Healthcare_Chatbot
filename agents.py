"""
Healthcare Agents - Multi-Agent System
Contains all agent definitions and LangGraph workflow
"""

from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END


# State definition for LangGraph
class AgentState(TypedDict):
    user_input: str
    symptom_analysis: str
    medication_advice: str
    home_remedies: str
    diet_lifestyle: str
    doctor_recommendations: str
    error: str


# Helper function to search Tavily
def search_tavily(tavily_client, query: str, max_results: int = 3) -> str:
    """Search Tavily API for verified health information"""
    if not tavily_client:
        return "Tavily client not initialized."
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        if response.get("results"):
            sources = []
            for result in response["results"]:
                title = result.get("title", "")
                content = result.get("content", "")
                url = result.get("url", "")
                sources.append(f"**{title}**\n{content}\nSource: {url}")
            return "\n\n".join(sources)
        return "No verified information found."
    except Exception as e:
        return f"Error fetching data: {str(e)}"


# Agent 1: Symptom Analyzer
def symptom_analyzer_agent(state: AgentState, llm, tavily_client) -> AgentState:
    """Analyze symptoms and identify possible conditions"""
    if not llm:
        state["symptom_analysis"] = "LLM not initialized."
        return state
    
    user_input = state["user_input"]
    
    # Search for verified information
    tavily_info = search_tavily(tavily_client, f"medical symptoms analysis {user_input}")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a clinical triage assistant. Use verified Tavily evidence to deliver a concise, non-repetitive assessment.

Output STRICTLY in this structure (markdown):

**Structured Symptom Analysis**
- **Summary:** • sentence 1 • sentence 2  (max 25 words total)
- **Possible Conditions:** markdown table with columns `Condition | Key Indicators | Likelihood` (3–4 rows, concise phrases)
- **Assessment:** markdown table with rows for `Severity`, `Red-Flag Risks`, `Who Needs Urgent Care`
- **Next Steps:** numbered list (max 4 items) combining home monitoring + escalation criteria (include temperature threshold + specific danger signs)

Rules:
- Keep total word count ≤ 220.
- Do not repeat medication, home-remedy, or doctor lists (other agents provide them).
- Reference Tavily evidence implicitly; no raw URLs.
- Never add extra sections or disclaimers.
"""),
        ("human", f"User symptoms: {user_input}\n\nVerified medical information:\n{tavily_info}\n\nProvide the Structured Symptom Analysis as specified.")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({})
        state["symptom_analysis"] = response.content
    except Exception as e:
        state["symptom_analysis"] = f"Error in symptom analysis: {str(e)}"
        state["error"] = str(e)
    
    return state


# Agent 2: Medication Agent
def medication_agent(state: AgentState, llm, tavily_client) -> AgentState:
    """Suggest medications with dosage, side effects, and precautions"""
    if not llm:
        state["medication_advice"] = "LLM not initialized."
        return state
    
    user_input = state["user_input"]
    symptom_analysis = state.get("symptom_analysis", "")
    
    # Enhanced search for medication information with multiple queries
    tavily_info1 = search_tavily(tavily_client, f"medication names brand names treatment {user_input} prescription drugs", max_results=5)
    tavily_info2 = search_tavily(tavily_client, f"medication dosage timing frequency {user_input} how to take", max_results=5)
    tavily_info = f"{tavily_info1}\n\n{tavily_info2}"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a clinical pharmacology assistant. Produce a concise, data-backed plan without repetition.

Requirements:
- Begin and end with the exact disclaimer: "⚠️ CONSULT A DOCTOR BEFORE TAKING ANY MEDICATION. This information is for educational purposes only."
- Limit to the top 3 evidence-backed medications (prioritize those appearing in Tavily results). If fewer than 3 are appropriate, list fewer.
- Present medications in a single markdown table with columns: `Medication (Generic / Brand) | When & How to Take | Adult Dose | Key Precautions | Common Side Effects | Rx Status`.
- Timing must include meal relation and time-of-day guidance when available. Keep each cell ≤ 25 words; no sub-bullets.
- After the table, add one short paragraph titled **Missed Dose & Duration** (≤ 40 words) summarizing course length and what to do if a dose is missed.
- Do NOT restate home remedies, lifestyle tips, or doctor information.
- No additional sections or repeated text.
"""),
        ("human", f"Symptoms: {user_input}\n\nSymptom Analysis:\n{symptom_analysis}\n\nVERIFIED MEDICATION INFORMATION FROM WEB SEARCH:\n{tavily_info}\n\nDeliver the concise table and summary as specified, using only medications supported by the verified information.")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({})
        state["medication_advice"] = response.content
    except Exception as e:
        state["medication_advice"] = f"Error in medication advice: {str(e)}"
        state["error"] = str(e)
    
    return state


# Agent 3: Home Remedies Agent
def home_remedies_agent(state: AgentState, llm, tavily_client) -> AgentState:
    """Suggest safe natural remedies and self-care practices"""
    if not llm:
        state["home_remedies"] = "LLM not initialized."
        return state
    
    user_input = state["user_input"]
    symptom_analysis = state.get("symptom_analysis", "")
    
    # Search for home remedies
    tavily_info = search_tavily(tavily_client, f"home remedies natural treatment {user_input} self-care")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a clinical self-care advisor. Produce a concise, evidence-backed plan without duplication or fluff.

Output format (markdown, ≤ 180 words):

**Home Remedies & Self-Care**
- Markdown table with columns `Remedy | How to Use | Why It Helps | Caution` (max 4 rows, ≤ 20 words per cell)
- **Stop Home Care If:** bullet list of 3 concrete escalation triggers (temperatures/symptoms)
- **Evidence Notes:** bullet list (max 2) citing source type (e.g., "WHO fever guidance", "Mayo Clinic patient sheet") without URLs

Rules:
- Mention only remedies supported by Tavily evidence.
- Do NOT repeat medication dosages, diet plans, or doctor advice.
- No additional sections, disclaimers, or repeated text.
"""),
        ("human", f"Symptoms: {user_input}\n\nSymptom Analysis:\n{symptom_analysis}\n\nVerified home remedy information:\n{tavily_info}\n\nProvide the structured response exactly as specified.")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({})
        state["home_remedies"] = response.content
    except Exception as e:
        state["home_remedies"] = f"Error in home remedies: {str(e)}"
        state["error"] = str(e)
    
    return state


# Agent 4: Diet & Lifestyle Advisor
def diet_lifestyle_agent(state: AgentState, llm, tavily_client) -> AgentState:
    """Provide diet, meal plans, and lifestyle recommendations"""
    if not llm:
        state["diet_lifestyle"] = "LLM not initialized."
        return state
    
    user_input = state["user_input"]
    symptom_analysis = state.get("symptom_analysis", "")
    
    # Search for diet and lifestyle information
    tavily_info = search_tavily(tavily_client, f"diet nutrition lifestyle recommendations {user_input} meal plan")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a clinical nutrition & lifestyle coach. Deliver a succinct plan tailored to the reported symptoms.

Output format (markdown, ≤ 220 words):
- **Hydration & Monitoring:** bullet list (max 3) with fluid targets and temperature-check cadence.
- **Day Plan Table:** table with columns `Meal Time | What to Eat | Why It Helps | Portion Tips` covering Breakfast, Lunch, Dinner, Snacks (≤ 18 words per cell).
- **Foods to Limit:** bullet list (max 4) focusing on items that hinder recovery.
- **Rest & Activity:** bullet list (max 3) for sleep, movement, environment (no overlap with other bullets).
- **Prevention After Recovery:** single sentence (≤ 20 words) highlighting one sustainable habit.

Rules:
- Do NOT repeat medication names, home remedies, or doctor contacts.
- Keep language direct; no duplicated advice.
- Reference Tavily evidence implicitly; no URLs.
"""),
        ("human", f"Symptoms: {user_input}\n\nSymptom Analysis:\n{symptom_analysis}\n\nVerified diet and lifestyle information:\n{tavily_info}\n\nProvide the structured response exactly as specified.")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({})
        state["diet_lifestyle"] = response.content
    except Exception as e:
        state["diet_lifestyle"] = f"Error in diet/lifestyle advice: {str(e)}"
        state["error"] = str(e)
    
    return state


# Agent 5: Doctor Recommendation Agent
def doctor_recommendation_agent(state: AgentState, llm, tavily_client) -> AgentState:
    """Suggest relevant specialists and telemedicine platforms"""
    if not llm:
        state["doctor_recommendations"] = "LLM not initialized."
        return state
    
    user_input = state["user_input"]
    symptom_analysis = state.get("symptom_analysis", "")
    
    # Enhanced search for doctor information with multiple queries
    tavily_info1 = search_tavily(tavily_client, f"doctor names specialists {user_input} healthcare providers hospitals", max_results=5)
    tavily_info2 = search_tavily(tavily_client, f"doctor appointment booking consultation hours availability {user_input}", max_results=5)
    tavily_info3 = search_tavily(tavily_client, f"telemedicine platforms online doctors {user_input} virtual consultation", max_results=5)
    tavily_info = f"{tavily_info1}\n\n{tavily_info2}\n\n{tavily_info3}"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a medical referral coordinator. Provide concise, non-redundant guidance using verified Tavily data.

Output format (markdown, ≤ 220 words):
- **Best Specialist Type & Why:** one sentence.
- **In-Person Options:** table with columns `Doctor / Facility | Specialty | Location | Key Hours | How to Book`. Include up to 4 rows drawn from Tavily results (≤ 18 words per cell, no duplicate facilities).
- **Telemedicine Options:** table with columns `Platform | Available Providers | Service Hours | Booking Method | Typical Wait`. Up to 3 rows.
- **Escalate Immediately If:** bullet list (max 3) noting concrete red-flag scenarios.
- **Emergency Access:** one sentence naming the 24/7 facility from search results.

Rules:
- Do NOT repeat medication, home-remedy, or diet advice.
- Mention each contact number or booking URL only once (omit full URLs; note “call” or “app”).
- Keep wording tight; no repeated phrases across rows.
"""),
        ("human", f"Symptoms: {user_input}\n\nSymptom Analysis:\n{symptom_analysis}\n\nVERIFIED DOCTOR AND HEALTHCARE INFORMATION FROM WEB SEARCH:\n{tavily_info}\n\nProvide the structured response exactly as specified, extracting real doctor/platform names and hours from the verified information.")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({})
        state["doctor_recommendations"] = response.content
    except Exception as e:
        state["doctor_recommendations"] = f"Error in doctor recommendations: {str(e)}"
        state["error"] = str(e)
    
    return state


# Build LangGraph workflow
def create_workflow(llm, tavily_client):
    """Create the LangGraph workflow with all agents"""
    
    # Create wrapper functions that include llm and tavily_client
    def symptom_wrapper(state):
        return symptom_analyzer_agent(state, llm, tavily_client)
    
    def medication_wrapper(state):
        return medication_agent(state, llm, tavily_client)
    
    def home_remedies_wrapper(state):
        return home_remedies_agent(state, llm, tavily_client)
    
    def diet_lifestyle_wrapper(state):
        return diet_lifestyle_agent(state, llm, tavily_client)
    
    def doctor_recommendation_wrapper(state):
        return doctor_recommendation_agent(state, llm, tavily_client)
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("symptom_analyzer", symptom_wrapper)
    workflow.add_node("medication", medication_wrapper)
    workflow.add_node("home_remedies", home_remedies_wrapper)
    workflow.add_node("diet_lifestyle", diet_lifestyle_wrapper)
    workflow.add_node("doctor_recommendation", doctor_recommendation_wrapper)
    
    # Define the flow
    workflow.set_entry_point("symptom_analyzer")
    workflow.add_edge("symptom_analyzer", "medication")
    workflow.add_edge("medication", "home_remedies")
    workflow.add_edge("home_remedies", "diet_lifestyle")
    workflow.add_edge("diet_lifestyle", "doctor_recommendation")
    workflow.add_edge("doctor_recommendation", END)
    
    return workflow.compile()

