"""Multi-agent healthcare workflow and offline fallbacks."""

from __future__ import annotations

import re
from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph


class AgentState(TypedDict):
    user_input: str
    symptom_analysis: str
    medication_advice: str
    home_remedies: str
    diet_lifestyle: str
    doctor_recommendations: str
    error: str


COMMON_SYMPTOM_STOPWORDS = {
    "and", "with", "for", "the", "have", "has", "had", "from", "that", "this",
    "after", "before", "been", "over", "under", "into", "your", "about", "feel",
    "feeling", "days", "day", "weeks", "week", "hours", "hour",
}


def extract_symptoms(user_input: str) -> list[str]:
    """Extract a small list of symptom phrases from free text."""
    chunks = re.split(r",|/|;|\band\b|\bwith\b", user_input.lower())
    symptoms: list[str] = []
    for chunk in chunks:
        cleaned = " ".join(re.findall(r"[a-z0-9']+", chunk))
        cleaned = re.sub(r"\b\d+\b", "", cleaned).strip()
        if not cleaned:
            continue
        words = [word for word in cleaned.split() if word not in COMMON_SYMPTOM_STOPWORDS]
        phrase = " ".join(words).strip()
        if phrase and phrase not in symptoms:
            symptoms.append(phrase)
    return symptoms[:4] or ["general illness symptoms"]


def has_red_flags(user_input: str) -> bool:
    red_flags = (
        "chest pain", "shortness of breath", "breathing trouble", "confusion",
        "seizure", "fainting", "severe dehydration", "blue lips", "stroke",
        "pregnant bleeding", "unconscious", "severe abdominal pain",
    )
    lowered = user_input.lower()
    return any(flag in lowered for flag in red_flags)


def likely_condition_rows(symptoms: list[str]) -> list[tuple[str, str, str]]:
    first = symptoms[0]
    rows = [
        ("Viral illness", f"{first}, fatigue, recent onset", "Moderate"),
        ("Upper respiratory infection", "fever, cough, sore throat, congestion", "Moderate"),
        ("Seasonal allergy or irritation", "mild symptoms without high fever", "Low"),
    ]
    if any("stomach" in symptom or "vomit" in symptom or "diarr" in symptom for symptom in symptoms):
        rows[1] = ("Stomach infection", "nausea, diarrhea, abdominal cramps", "Moderate")
    if any("headache" in symptom for symptom in symptoms):
        rows.append(("Tension or migraine pattern", "headache, light sensitivity, stress triggers", "Low-Moderate"))
    return rows[:4]


def fallback_symptom_analysis(user_input: str) -> str:
    symptoms = extract_symptoms(user_input)
    severity = "High" if has_red_flags(user_input) else "Moderate"
    urgent_group = (
        "Anyone with chest pain, breathing trouble, confusion, seizures, or worsening dehydration."
        if severity == "High"
        else "People with persistent fever above 103 F, dehydration, or rapidly worsening symptoms."
    )
    possible_rows = "\n".join(
        f"| {condition} | {indicators} | {likelihood} |"
        for condition, indicators, likelihood in likely_condition_rows(symptoms)
    )
    return (
        "**Structured Symptom Analysis**\n"
        f"- **Summary:** Symptoms suggest {', '.join(symptoms[:2])}. Monitor trend, hydration, fever, and any breathing or mental-status change.\n"
        "- **Possible Conditions:**\n"
        "| Condition | Key Indicators | Likelihood |\n"
        "| --- | --- | --- |\n"
        f"{possible_rows}\n"
        "- **Assessment:**\n"
        "| Item | Details |\n"
        "| --- | --- |\n"
        f"| Severity | {severity} |\n"
        "| Red-Flag Risks | Breathing trouble, confusion, severe weakness, dehydration, chest pain |\n"
        f"| Who Needs Urgent Care | {urgent_group} |\n"
        "- **Next Steps:**\n"
        "1. Rest, drink fluids, and recheck temperature every 4 to 6 hours.\n"
        "2. Seek urgent care if fever stays above 103 F, breathing worsens, or new confusion appears.\n"
        "3. Use the medication and self-care sections for supportive care only.\n"
        "4. Arrange a clinician review if symptoms persist beyond 2 to 3 days or worsen sooner."
    )


def fallback_medication_advice(user_input: str) -> str:
    symptoms = extract_symptoms(user_input)
    needs_cough = any("cough" in symptom for symptom in symptoms)
    needs_nausea = any("nausea" in symptom or "vomit" in symptom for symptom in symptoms)
    third_med = (
        "| Oral rehydration solution / Electral | Sip after each loose stool or vomiting episode | 200 to 250 mL per episode | Use carefully in kidney or heart failure | Bloating, nausea | OTC |"
        if needs_nausea
        else "| Cetirizine / Zyrtec | Once daily in the evening for allergy-like symptoms | 10 mg once daily | May cause drowsiness; avoid alcohol | Sleepiness, dry mouth | OTC |"
    )
    second_med = (
        "| Dextromethorphan syrup / Benadryl DR | Use for troublesome dry cough, mainly at night | Follow label dose | Avoid combining with sedatives or MAOIs | Drowsiness, dizziness | OTC |"
        if needs_cough
        else "| Ibuprofen / Advil | Take with food for body pain if tolerated | 200 to 400 mg every 6 to 8 hours | Avoid in ulcers, kidney disease, dehydration | Acidity, stomach upset | OTC |"
    )
    return (
        "IMPORTANT: CONSULT A DOCTOR BEFORE TAKING ANY MEDICATION. This information is for educational purposes only.\n\n"
        "| Medication (Generic / Brand) | When & How to Take | Adult Dose | Key Precautions | Common Side Effects | Rx Status |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| Paracetamol / Crocin | After food or with water for fever or pain | 500 to 650 mg every 6 to 8 hours | Avoid exceeding daily label maximum; caution in liver disease | Nausea, rash | OTC |\n"
        f"{second_med}\n"
        f"{third_med}\n\n"
        "**Missed Dose & Duration** Use symptom-relief medicines only when needed for 1 to 3 days. If you miss a dose, take it when remembered unless the next dose is soon due.\n\n"
        "IMPORTANT: CONSULT A DOCTOR BEFORE TAKING ANY MEDICATION. This information is for educational purposes only."
    )


def fallback_home_remedies(user_input: str) -> str:
    symptoms = extract_symptoms(user_input)
    steam_row = (
        "| Warm steam inhalation | 5 to 10 minutes once or twice daily | May ease congestion and throat irritation | Avoid very hot steam, especially for children |"
        if any("cold" in symptom or "cough" in symptom or "congestion" in symptom for symptom in symptoms)
        else "| Lukewarm sponge and light clothing | Use during fever discomfort | Helps body cooling and comfort | Stop if shivering increases |"
    )
    return (
        "**Home Remedies & Self-Care**\n"
        "| Remedy | How to Use | Why It Helps | Caution |\n"
        "| --- | --- | --- | --- |\n"
        "| Water or oral fluids | Small frequent sips through the day | Prevents dehydration and fatigue | Seek care if unable to keep fluids down |\n"
        "| Warm soups or bland meals | Eat simple foods in small portions | Supports energy without irritating the stomach | Avoid greasy or very spicy meals |\n"
        f"{steam_row}\n"
        "| Rest in a cool, ventilated room | Reduce activity for 24 to 48 hours | Supports recovery and symptom monitoring | Do not ignore worsening symptoms |\n"
        "- **Stop Home Care If:**\n"
        "- Fever rises above 103 F or lasts more than 3 days.\n"
        "- Breathing trouble, chest pain, confusion, or severe weakness develops.\n"
        "- Vomiting, diarrhea, or poor intake causes dehydration.\n"
        "- **Evidence Notes:**\n"
        "- General fever and hydration guidance from standard patient-care sources.\n"
        "- Escalation thresholds based on common urgent-care triage practice."
    )


def fallback_diet_lifestyle(user_input: str) -> str:
    symptoms = extract_symptoms(user_input)
    snack = "banana, toast, crackers" if any("stomach" in s or "nausea" in s or "diarr" in s for s in symptoms) else "fruit, yogurt, nuts"
    return (
        "- **Hydration & Monitoring:**\n"
        "- Aim for 2 to 3 liters of fluids daily unless a clinician told you to restrict fluids.\n"
        "- Check temperature every 4 to 6 hours while fever or chills continue.\n"
        "- Track urine output, appetite, and any worsening breathing or pain.\n"
        "- **Day Plan Table:**\n"
        "| Meal Time | What to Eat | Why It Helps | Portion Tips |\n"
        "| --- | --- | --- | --- |\n"
        "| Breakfast | Oats, toast, fruit, warm tea | Gentle energy and hydration | Keep portions light |\n"
        "| Lunch | Rice, dal, soup, cooked vegetables | Easy digestion and recovery support | Eat slowly |\n"
        "| Dinner | Khichdi, broth, soft protein | Maintains calories without heaviness | Choose smaller servings |\n"
        f"| Snacks | {snack} | Maintains intake between meals | Small frequent portions |\n"
        "- **Foods to Limit:**\n"
        "- Fried or oily foods.\n"
        "- Alcohol and smoking.\n"
        "- Very spicy meals if nausea or throat irritation is present.\n"
        "- Excess caffeine if you are dehydrated or sleeping poorly.\n"
        "- **Rest & Activity:**\n"
        "- Sleep 7 to 9 hours and add daytime rest if feverish.\n"
        "- Avoid intense exercise until fever and weakness resolve.\n"
        "- Keep the room cool, clean, and well ventilated.\n"
        "- **Prevention After Recovery:** Resume normal activity gradually and maintain hand hygiene plus adequate sleep."
    )


def fallback_doctor_recommendations(user_input: str) -> str:
    specialist = "General physician or internal medicine doctor" if not has_red_flags(user_input) else "Emergency physician or urgent-care clinician"
    why = "best for first evaluation, testing, and deciding whether specialist care is needed"
    return (
        f"- **Best Specialist Type & Why:** {specialist} is the best first contact because it is the {why}.\n"
        "- **In-Person Options:**\n"
        "| Doctor / Facility | Specialty | Location | Key Hours | How to Book |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Nearby primary care clinic | General medicine | Local area | Daytime OPD hours | Call reception |\n"
        "| Multispecialty hospital OPD | Internal medicine | Nearest city hub | Morning and evening slots | Hospital desk or app |\n"
        "| Urgent care center | Acute illness review | Nearby urgent-care facility | Extended evening hours | Walk in or call |\n"
        "| Emergency department | Emergency medicine | 24/7 hospital | Open all day | Direct arrival |\n"
        "- **Telemedicine Options:**\n"
        "| Platform | Available Providers | Service Hours | Booking Method | Typical Wait |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Hospital teleconsultation portal | General physicians | Usually daytime | App or website | Same day |\n"
        "| National telehealth service | Primary care doctors | Extended hours | Phone or app | 15 to 60 min |\n"
        "| Insurance doctor line | Network clinicians | Depends on insurer | Call center | Varies |\n"
        "- **Escalate Immediately If:**\n"
        "- Breathing difficulty, chest pain, bluish lips, or fainting starts.\n"
        "- Confusion, seizure, persistent vomiting, or severe dehydration appears.\n"
        "- Fever remains very high or symptoms worsen rapidly despite supportive care.\n"
        "- **Emergency Access:** Use the nearest 24/7 hospital emergency department if any red-flag symptoms appear."
    )


def search_tavily(tavily_client, query: str, max_results: int = 2) -> str:
    """Search Tavily API for verified health information."""
    if not tavily_client:
        return "Tavily client not initialized."
    try:
        response = tavily_client.search(query=query, search_depth="basic", max_results=max_results)
        if response.get("results"):
            sources = []
            for result in response["results"]:
                title = result.get("title", "")
                content = result.get("content", "")[:500]
                url = result.get("url", "")
                sources.append(f"**{title}**\n{content}...\nSource: {url}")
            return "\n\n".join(sources)
        return "No verified information found."
    except Exception as exc:
        return f"Error fetching data: {str(exc)}"


def symptom_analyzer_agent(state: AgentState, llm, tavily_client) -> AgentState:
    """Analyze symptoms and identify possible conditions."""
    if not llm:
        state["symptom_analysis"] = fallback_symptom_analysis(state["user_input"])
        state["error"] = "Live symptom analysis unavailable; offline guidance used."
        return state

    user_input = state["user_input"]
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
        ("human", "Symptoms: {symptoms}\n\nVerified information:\n{info}\n\nProvide the structured response exactly as specified."),
    ])

    try:
        response = (prompt | llm).invoke({"symptoms": user_input, "info": tavily_info})
        state["symptom_analysis"] = response.content
    except Exception as exc:
        state["symptom_analysis"] = fallback_symptom_analysis(user_input)
        state["error"] = f"Live symptom analysis unavailable; offline guidance used. {str(exc)}"

    return state


def medication_agent(state: AgentState, llm, tavily_client) -> AgentState:
    """Provide high-level medication guidance."""
    if not llm:
        state["medication_advice"] = fallback_medication_advice(state["user_input"])
        state["error"] = "Live medication advice unavailable; offline guidance used."
        return state

    user_input = state["user_input"]
    symptom_analysis = state.get("symptom_analysis", "")
    tavily_info = search_tavily(tavily_client, f"OTC medication advice precautions adult dose {user_input}")
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a medication-information assistant. Provide concise, non-prescriptive OTC-oriented educational guidance.

Output format (markdown, ≤ 220 words):
- Start with this exact sentence: `IMPORTANT: CONSULT A DOCTOR BEFORE TAKING ANY MEDICATION. This information is for educational purposes only.`
- Then a markdown table with columns `Medication (Generic / Brand) | When & How to Take | Adult Dose | Key Precautions | Common Side Effects | Rx Status`
- Include 3 rows maximum, concise wording, mostly OTC where appropriate.
- End with one short paragraph titled `**Missed Dose & Duration**`.
- Repeat the exact IMPORTANT sentence once again at the end.

Rules:
- Do not mention treatments that need specialist monitoring unless clearly labeled Rx.
- Avoid duplicate wording across rows.
- No URLs.
"""),
        ("human", "Symptoms: {symptoms}\n\nSymptom Analysis:\n{analysis}\n\nVerified medication information:\n{info}\n\nProvide the structured response exactly as specified."),
    ])

    try:
        response = (prompt | llm).invoke({"symptoms": user_input, "analysis": symptom_analysis, "info": tavily_info})
        state["medication_advice"] = response.content
    except Exception as exc:
        state["medication_advice"] = fallback_medication_advice(user_input)
        state["error"] = f"Live medication advice unavailable; offline guidance used. {str(exc)}"

    return state


def home_remedies_agent(state: AgentState, llm, tavily_client) -> AgentState:
    """Provide home remedy and self-care guidance."""
    if not llm:
        state["home_remedies"] = fallback_home_remedies(state["user_input"])
        state["error"] = "Live home-remedy guidance unavailable; offline guidance used."
        return state

    user_input = state["user_input"]
    tavily_info = search_tavily(tavily_client, f"home remedies self care hydration rest advice {user_input}")
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a self-care assistant. Keep output concise and practical.

Output format (markdown, ≤ 220 words):
**Home Remedies & Self-Care**
| Remedy | How to Use | Why It Helps | Caution |
| --- | --- | --- | --- |
3 to 4 rows only.
- **Stop Home Care If:** bullet list with max 3 items.
- **Evidence Notes:** bullet list with max 2 items.

Rules:
- Focus on hydration, rest, symptom comfort, and escalation.
- Do not repeat medications or doctor lists.
- No URLs.
"""),
        ("human", "Symptoms: {symptoms}\n\nVerified self-care information:\n{info}\n\nProvide the structured response exactly as specified."),
    ])

    try:
        response = (prompt | llm).invoke({"symptoms": user_input, "info": tavily_info})
        state["home_remedies"] = response.content
    except Exception as exc:
        state["home_remedies"] = fallback_home_remedies(user_input)
        state["error"] = f"Live home-remedy guidance unavailable; offline guidance used. {str(exc)}"

    return state


def diet_lifestyle_agent(state: AgentState, llm, tavily_client) -> AgentState:
    """Provide diet and lifestyle guidance."""
    if not llm:
        state["diet_lifestyle"] = fallback_diet_lifestyle(state["user_input"])
        state["error"] = "Live diet/lifestyle advice unavailable; offline guidance used."
        return state

    user_input = state["user_input"]
    symptom_analysis = state.get("symptom_analysis", "")
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
        ("human", "Symptoms: {symptoms}\n\nSymptom Analysis:\n{analysis}\n\nVerified diet and lifestyle information:\n{info}\n\nProvide the structured response exactly as specified."),
    ])

    try:
        response = (prompt | llm).invoke({"symptoms": user_input, "analysis": symptom_analysis, "info": tavily_info})
        state["diet_lifestyle"] = response.content
    except Exception as exc:
        state["diet_lifestyle"] = fallback_diet_lifestyle(user_input)
        state["error"] = f"Live diet/lifestyle advice unavailable; offline guidance used. {str(exc)}"

    return state


def doctor_recommendation_agent(state: AgentState, llm, tavily_client) -> AgentState:
    """Suggest relevant specialists and telemedicine platforms."""
    if not llm:
        state["doctor_recommendations"] = fallback_doctor_recommendations(state["user_input"])
        state["error"] = "Live doctor recommendations unavailable; offline guidance used."
        return state

    user_input = state["user_input"]
    symptom_analysis = state.get("symptom_analysis", "")
    tavily_info1 = search_tavily(tavily_client, f"doctor names specialists {user_input} healthcare providers hospitals", max_results=2)
    tavily_info2 = search_tavily(tavily_client, f"doctor appointment booking consultation hours availability {user_input}", max_results=2)
    tavily_info3 = search_tavily(tavily_client, f"telemedicine platforms online doctors {user_input} virtual consultation", max_results=2)
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
        ("human", "Symptoms: {symptoms}\n\nSymptom Analysis:\n{analysis}\n\nVERIFIED DOCTOR AND HEALTHCARE INFORMATION FROM WEB SEARCH:\n{info}\n\nProvide the structured response exactly as specified, extracting real doctor/platform names and hours from the verified information."),
    ])

    try:
        response = (prompt | llm).invoke({"symptoms": user_input, "analysis": symptom_analysis, "info": tavily_info})
        state["doctor_recommendations"] = response.content
    except Exception as exc:
        state["doctor_recommendations"] = fallback_doctor_recommendations(user_input)
        state["error"] = f"Live doctor recommendations unavailable; offline guidance used. {str(exc)}"

    return state


def create_workflow(llm, tavily_client):
    """Create the LangGraph workflow with all agents."""
    workflow = StateGraph(AgentState)
    workflow.add_node("symptom_analyzer_node", lambda state: symptom_analyzer_agent(state, llm, tavily_client))
    workflow.add_node("medication_node", lambda state: medication_agent(state, llm, tavily_client))
    workflow.add_node("home_remedies_node", lambda state: home_remedies_agent(state, llm, tavily_client))
    workflow.add_node("diet_lifestyle_node", lambda state: diet_lifestyle_agent(state, llm, tavily_client))
    workflow.add_node("doctor_recommendation_node", lambda state: doctor_recommendation_agent(state, llm, tavily_client))
    workflow.set_entry_point("symptom_analyzer_node")
    workflow.add_edge("symptom_analyzer_node", "medication_node")
    workflow.add_edge("medication_node", "home_remedies_node")
    workflow.add_edge("home_remedies_node", "diet_lifestyle_node")
    workflow.add_edge("diet_lifestyle_node", "doctor_recommendation_node")
    workflow.add_edge("doctor_recommendation_node", END)
    return workflow.compile()
