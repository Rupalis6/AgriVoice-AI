import streamlit as st
import os
from io import BytesIO
from gtts import gTTS
from groq import Groq
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder
# Load API key from the local .env file automatically
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
st.set_page_config(page_title="AgriVoice AI", page_icon="🌾", layout="wide")

# --------------------------------------------------
# LANGUAGE CONFIGURATION
# --------------------------------------------------
lang_map = {"English": "en", "हिन्दी": "hi", "मराठी": "mr"}

# --------------------------------------------------
# GROQ AI CLIENT
# --------------------------------------------------
@st.cache_resource
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

client = get_groq_client()

# --------------------------------------------------
# KNOWLEDGE BASE
# --------------------------------------------------
KB = [
    {
        "topic": "Cotton yellow leaves",
        "keywords": ["cotton", "yellow leaves", "yellowing", "पिवळी पाने", "कपास", "पीले पत्ते", "कापूस", "पिवळी"],
        "en": "Yellow leaves in cotton can be caused by nutrient deficiency, water stress, root problems, or pests. Check soil moisture and inspect the underside of leaves. Avoid applying pesticide until the cause is identified.",
        "hi": "कपास में पत्ते पीले होना पोषक तत्वों की कमी, पानी की समस्या, जड़ों या कीटों के कारण हो सकता है। मिट्टी की नमी जांचें और पत्तों के नीचे कीट देखें। कारण पहचानने से पहले कीटनाशक न डालें।",
        "mr": "कापसाची पाने पिवळी होणे हे पोषक घटकांची कमतरता, पाण्याचा ताण, मुळांची समस्या किंवा किडींमुळे होऊ शकते. जमिनीतील ओलावा तपासा आणि पानांच्या खालच्या बाजूस किडी पाहा. कारण समजल्याशिवाय कीटकनाशक वापरू नका.",
        "source": "General crop-care guidance; confirm with local KVK/agriculture officer"
    },
    {
        "topic": "Aphids",
        "keywords": ["aphid", "aphids", "मावा", "मावा कीड"],
        "en": "Aphids are small sap-sucking insects often found on tender shoots and leaf undersides. Inspect the crop regularly and consult a local agricultural officer for a crop- and region-specific control recommendation before using chemicals.",
        "hi": "माहू छोटे रस चूसने वाले कीट हैं, जो नई टहनियों और पत्तों के नीचे मिल सकते हैं। फसल की नियमित जांच करें और रसायन इस्तेमाल करने से पहले स्थानीय कृषि अधिकारी से फसल व क्षेत्र के अनुसार सलाह लें।",
        "mr": "मावा ही लहान रस शोषणारी कीड असून कोवळ्या फांद्यांवर व पानांच्या खालच्या बाजूस आढळते. पिकाची नियमित तपासणी करा आणि रासायनिक उपाय करण्यापूर्वी स्थानिक कृषी अधिकाऱ्यांचा सल्ला घ्या.",
        "source": "General pest information; local advisory required for treatment"
    },
    {
        "topic": "Soil testing",
        "keywords": ["soil test", "soil testing", "soil health", "माती परीक्षण", "मिट्टी जांच"],
        "en": "Soil testing helps determine pH and nutrient levels so fertilizer can be selected more accurately. Collect representative soil samples following your local agriculture department instructions and submit them to a soil testing laboratory.",
        "hi": "मिट्टी परीक्षण से pH और पोषक तत्वों का स्तर पता चलता है, जिससे उर्वरक का चयन बेहतर होता है। स्थानीय कृषि विभाग के निर्देशों के अनुसार नमूना लेकर मिट्टी परीक्षण प्रयोगशाला में दें।",
        "mr": "माती परीक्षणामुळे pH आणि पोषक घटकांची पातळी समजते व योग्य खत निवडण्यास मदत होते. स्थानिक कृषी विभागाच्या सूचनेनुसार मातीचा नमुना घेऊन प्रयोगशाळेत द्या.",
        "source": "Soil testing general guidance; local agriculture department/lab"
    },
    {
        "topic": "Crop watering",
        "keywords": ["water", "watering", "irrigation", "पाणी", "सिंचन", "पानी"],
        "en": "Irrigation frequency depends on crop, soil type, growth stage, temperature, and rainfall. Check soil moisture before irrigating and avoid waterlogging. For a precise schedule, share your crop, location, and growth stage.",
        "hi": "सिंचाई की मात्रा फसल, मिट्टी, अवस्था, तापमान और बारिश पर निर्भर करती है। सिंचाई से पहले मिट्टी की नमी जांचें और जलभराव से बचें। सही सलाह के लिए फसल, स्थान और अवस्था बताएं।",
        "mr": "पाणी देण्याची वारंवारता पीक, मातीचा प्रकार, वाढीची अवस्था, तापमान आणि पावसावर अवलंबून असते. पाणी देण्यापूर्वी ओलावा तपासा व पाणी साचू देऊ नका. योग्य मार्गदर्शनासाठी पीक, ठिकाण आणि अवस्था सांगा.",
        "source": "General irrigation guidance"
    },
    {
        "topic": "Government schemes",
        "keywords": ["scheme", "government", "subsidy", "yojana", "योजना", "अनुदान", "सरकारी योजना"],
        "en": "Government scheme eligibility and deadlines change. Tell me your state and the scheme name to help identify what information you need. Verify eligibility, dates, and required documents on the official government portal or with your agriculture office.",
        "hi": "सरकारी योजनाओं की पात्रता और अंतिम तिथियां बदल सकती हैं। अपना राज्य और योजना का नाम बताएं। पात्रता, तारीख और दस्तावेज आधिकारिक पोर्टल या कृषि कार्यालय से सत्यापित करें।",
        "mr": "सरकारी योजनांची पात्रता व अंतिम तारखा बदलू शकतात. तुमचे राज्य आणि योजनेचे नाव सांगा. पात्रता, तारीख व कागदपत्रे अधिकृत पोर्टल किंवा कृषी कार्यालयातून तपासा.",
        "source": "Official scheme portal/agriculture office must be checked for current details"
    },
    {
        "topic": "Mandi price",
        "keywords": ["mandi", "market price", "price", "rate", "भाव", "बाजारभाव", "मंडी"],
        "en": "Mandi prices change daily and vary by market, commodity quality, and arrival volume. This demo does not have a live price feed. Check Agmarknet or e-NAM and compare the market name and date before making a selling decision.",
        "hi": "मंडी भाव रोज बदलते हैं और बाजार, गुणवत्ता तथा आवक पर निर्भर करते हैं। इस डेमो में लाइव भाव उपलब्ध नहीं हैं। बेचने से पहले Agmarknet या e-NAM पर बाजार और तारीख जांचें।",
        "mr": "बाजारभाव रोज बदलतात आणि बाजार, मालाचा दर्जा व आवक यानुसार फरक पडतो. या डेमोमध्ये थेट भाव उपलब्ध नाहीत. विक्रीपूर्वी Agmarknet किंवा e-NAM वर बाजार आणि तारीख तपासा.",
        "source": "Agmarknet / e-NAM (live lookup not enabled in this prototype)"
    },
    {
        "topic": "Weather",
        "keywords": ["weather", "rain", "forecast", "पाऊस", "हवामान", "मौसम", "बारिश"],
        "en": "Weather information is not live in this demo. Check the India Meteorological Department (IMD) forecast for your district before irrigation, spraying, or harvesting decisions.",
        "hi": "इस डेमो में मौसम की लाइव जानकारी नहीं है। सिंचाई, छिड़काव या कटाई से पहले अपने जिले का India Meteorological Department (IMD) पूर्वानुमान देखें।",
        "mr": "या डेमोमध्ये थेट हवामान माहिती नाही. सिंचन, फवारणी किंवा कापणीपूर्वी तुमच्या जिल्ह्याचा India Meteorological Department (IMD) अंदाज तपासा.",
        "source": "India Meteorological Department (IMD); live weather lookup not enabled"
    }
]

# --------------------------------------------------
# KNOWLEDGE RETRIEVAL
# --------------------------------------------------
def retrieve(query):
    q = query.lower()
    scored = []
    for item in KB:
        score = sum(1 for keyword in item["keywords"] if keyword.lower() in q)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored else None

# --------------------------------------------------
# AI RESPONSE GENERATION - ALWAYS RETURNS 3 VALUES
# --------------------------------------------------
def generate_ai_answer(query, language):
    if client is None:
        return (
            "Groq API key is missing. Please configure GROQ_API_KEY.",
            "AI unavailable",
            "Missing API key"
        )

    item = retrieve(query)
    context = ""
    if item:
        context = f"""
Relevant agriculture knowledge-base context:
Topic: {item['topic']}
Information: {item[language]}
Reference: {item['source']}
Use this context when relevant. Do not imply it is a live or officially verified source.
"""

    language_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(language, "English")

    system_prompt = f"""
You are AgriVoice AI, a multilingual agricultural assistant for Indian farmers.
Respond in {language_name}.

Rules:
1. Use simple words farmers can understand.
2. Keep answers clear, practical, and reasonably short.
3. Give steps when helpful.
4. Do not invent scientific facts or government scheme details.
5. Never invent pesticide names, chemical combinations, application rates, or dosage.
6. For live weather, mandi prices, scheme deadlines, or current information, state that live data is not connected.
7. If uncertain, clearly say so rather than guessing.
8. Recommend KVK or a local agriculture officer for serious or unclear crop issues.
9. Never claim information has been verified unless it actually has.
10. Do not overstate the knowledge-base context.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Farmer's question:\n{query}\n\n{context}\n\nAnswer the farmer's question."
                }
            ],
            temperature=0.3,
            max_tokens=700
        )

        answer = response.choices[0].message.content or "I could not generate an answer. Please try again."

        if item:
            topic = item["topic"]
            source = item["source"]
        else:
            topic = "General agriculture question"
            source = "AI-generated guidance; verify with local agricultural experts"

        return answer, topic, source

    except Exception as e:
        # Keep the UI functional while returning the same 3-value structure.
        return (
            "Sorry, I am unable to generate an answer right now. Please try again or contact your local agricultural expert.",
            "AI error",
            f"Groq API unavailable ({type(e).__name__})"
        )

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div style="text-align:center">
<h1>🌾 AgriVoice AI</h1>
<p>Voice-First Multilingual Agricultural Assistant</p>
</div>
""", unsafe_allow_html=True)

st.caption("AI-powered agricultural guidance in English, Hindi and Marathi.")
st.info("Prototype: AI responses are informational. Always verify important agricultural decisions with local experts.")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.header("👨‍🌾 Farmer Settings")
    language = st.selectbox("Choose language / भाषा / भाषा", list(lang_map.keys()))
    st.markdown("### 🌱 Ask about")
    st.write("Crop care · Pest guidance · Government schemes · Market prices · Weather · Soil health")
    st.warning("For pesticide dosage or chemical use, consult a local agriculture officer/KVK and follow the official product label.")

# --------------------------------------------------
# QUESTION INPUT
# --------------------------------------------------

# --------------------------------------------------
# VOICE INPUT + QUESTION INPUT
# --------------------------------------------------

st.markdown("## 🎙️ Ask AgriVoice AI")

st.write("Speak your farming question or type it below.")

audio_bytes = audio_recorder(
    text="Click to record your question",
    recording_color="#e74c3c",
    neutral_color="#2e8b57",
    icon_name="microphone",
    icon_size="2x",
)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

    if st.button("📝 Convert Speech to Text"):
        try:
            with st.spinner("Listening and converting your speech..."):

                transcription = client.audio.transcriptions.create(
                    file=("farmer_question.wav", audio_bytes),
                    model="whisper-large-v3-turbo",
                    language=lang_map[language],
                    response_format="text",
                    temperature=0
                )

                transcribed_text = transcription.strip()

                st.session_state["question_input"] = transcribed_text

                st.success("Speech converted successfully!")

        except Exception as e:
            st.error(f"Speech recognition failed: {e}")

query = st.text_input(
    "Your question",
    placeholder="Type your farming question here...",
    key="question_input"
)

if st.button("🌱 Get AI Advice", type="primary") and query.strip():

    with st.spinner("AgriVoice AI is thinking..."):

        language_code = lang_map[language]

        response, topic, source = generate_ai_answer(
            query,
            language_code
        )

        st.session_state["last_response"] = response
        st.session_state["last_source"] = source
        st.session_state["last_topic"] = topic
        st.session_state["last_language"] = language_code


# --------------------------------------------------
# AI RESPONSE
# --------------------------------------------------
if "last_response" in st.session_state:
    st.markdown("## 🌿 AI Agricultural Advice")
    st.success(st.session_state["last_response"])
    st.caption(f"Topic: {st.session_state.get('last_topic', '')}")
    st.caption(f"Information source: {st.session_state.get('last_source', '')}")

    if st.button("🔊 Listen to Answer"):
        try:
            audio = BytesIO()
            gTTS(text=st.session_state["last_response"], lang=st.session_state["last_language"]).write_to_fp(audio)
            st.audio(audio.getvalue(), format="audio/mp3")
        except Exception:
            st.warning("Text-to-speech failed. Please check your internet connection or language support.")

# --------------------------------------------------
# DEMO QUESTIONS
# --------------------------------------------------
st.divider()
st.markdown("## 🎙️ Voice Input")
st.write("Voice input transcription is not yet enabled. You can currently type your question and listen to the AI response.")

st.markdown("## 🧪 Try These Questions")
sample_questions = [
    "Why are cotton leaves turning yellow?",
    "How can I identify aphids?",
    "How can I improve soil health?",
    "How often should I water my crops?",
    "How do I check government scheme eligibility?",
    "How can I increase wheat production?",
    "What causes fungal diseases in crops?",
    "How can I protect my crops during heavy rain?"
]
for sample in sample_questions:
    st.markdown(f"• {sample}")

st.divider()
st.caption("AgriVoice AI | Multilingual Agricultural Assistant | Prototype")
