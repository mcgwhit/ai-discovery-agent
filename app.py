import os
import json
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI Discovery Agent", layout="centered")
st.title("AI Discovery Agent — v1.1 (Structured)")

st.info("Human review required: Outputs are advisory only and should be reviewed before being shared with customers or used for commitments")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

notes = st.text_area("Paste discovery notes here:", height=240)

SYSTEM = """
You are a senior B2B Solutions Consultant. Convert messy discovery notes into a precise, structured brief.
Be cautious: do not invent facts. If something is missing, write it as an open question.

Return ONLY valid JSON matching this schema:
{
  "problems": ["..."],
  "success_metrics": ["..."],
  "requirements": {
    "functional": ["..."],
    "technical": ["..."],
    "security_compliance": ["..."]
  },
  "risks_red_flags": ["..."],
  "open_questions": ["..."],
  "demo_agenda": ["..."],
  "missing_info": ["..."]
  "deal_fit_score": "low | medium | high"
  "confidence_level": low | medium | high"
}
"""

def to_json(text: str) -> dict:
    # Try to parse as JSON; if model adds extra text, attempt a recovery.
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise

if st.button("Analyze"):
    if not notes.strip():
        st.warning("Paste some notes first.")
        st.stop()

    with st.spinner("Analyzing..."):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": notes},
            ],
        )

    raw = resp.choices[0].message.content
    try:
        data = to_json(raw)
        st.subheader("Deal fit score")
        st.write(data.get("deal_fit_score", "unknown"))
        st.subheader("Confidence level")
        st.write(data.get("confidence_level", "unknown"))
    except Exception:
        st.error("Could not parse model output as JSON. Here is the raw output:")
        st.code(raw)
        st.stop()

    st.subheader("Problems")
    st.write(data.get("problems", []))

    st.subheader("Success metrics")
    st.write(data.get("success_metrics", []))

    st.subheader("Requirements")
    req = data.get("requirements", {})
    st.markdown("**Functional**")
    st.write(req.get("functional", []))
    st.markdown("**Technical**")
    st.write(req.get("technical", []))
    st.markdown("**Security / Compliance**")
    st.write(req.get("security_compliance", []))

    st.subheader("Risks / red flags")
    st.write(data.get("risks_red_flags", []))

    st.subheader("Open questions")
    st.write(data.get("open_questions", []))

    st.subheader("Missing info")
    st.write(data.get("missing_info",[]))

    st.subheader("Demo agenda")
    st.write(data.get("demo_agenda", []))

