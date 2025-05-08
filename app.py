import streamlit as st
import anthropic
import os
from dotenv import load_dotenv
import time
import json
import re
from datetime import datetime
import random
import uuid
import base64
from io import BytesIO
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

import base64
from io import BytesIO
import requests


# Load environment variables
load_dotenv()

# Get API keys from .env
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]

# Configure page
st.set_page_config(
    page_title="FinBiz Business Assistant",
    page_icon="🇫🇮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling - enhanced for visual appeal
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 0.75rem;
    }
    .chat-message.user {
        background-color: #e9f0f8;
        border-left: 4px solid #0066CC;
    }
    .chat-message.assistant {
        background-color: #f4f9ff;
        border-left: 4px solid #00A3E0;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        background-color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .chat-message .message {
        flex: 1;
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 10px;
    }
    /* Button styling for equal dimensions */
    .stButton > button {
        border-radius: 10px;
        padding: 0.5rem 1rem;
        background-color: #0066CC;
        color: white;
        font-weight: bold;
        width: 100%; /* Full width buttons */
        height: 44px; /* Fixed height for all buttons */
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 5px;
        line-height: 1.2;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #004C99;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .model-buttons {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 15px;
    }
    .stSidebar {
        background-color: #f0f2f5;
        padding: 2rem 1rem;
        border-right: 1px solid #e0e0e0;
    }
    .sidebar-title {
        text-align: center;
        font-weight: bold;
        margin-bottom: 2rem;
        color: #0066CC;
    }
    .css-18e3th9 {
        padding-top: 2rem;
    }
    .model-option {
        display: flex;
        align-items: center;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
    }
    .model-option:hover {
        background-color: rgba(0,0,0,0.05);
    }
    .model-option.selected {
        background-color: rgba(0, 102, 204, 0.2);
        border-left: 3px solid #0066CC;
    }
    .model-icon {
        width: 30px;
        height: 30px;
        margin-right: 10px;
    }
    .welcome-card {
        background-color: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
        border-top: 5px solid #0066CC;
    }
    .welcome-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .welcome-icon {
        font-size: 2rem;
        margin-right: 1rem;
        color: #0066CC;
    }
    .followup-questions {
        margin-top: 1rem;
    }
    .followup-button {
        margin: 0.2rem 0;
        padding: 0.5rem;
        background-color: #f0f7ff;
        border: 1px solid #d0e3ff;
        border-radius: 8px;
        text-align: left;
        transition: background-color 0.3s;
        width: 100%;
        height: auto;
        min-height: 44px;
        color: #0066CC;
        cursor: pointer;
    }
    .followup-button:hover {
        background-color: #e0f0ff;
    }
    .reference {
        color: #0066CC;
        font-weight: bold;
    }
    .info-box {
        background-color: #f4f9ff;
        border-left: 4px solid #00A3E0;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 4px 4px 0;
    }
    .tip-box {
        background-color: #f2fff5;
        border-left: 4px solid #00C853;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 4px 4px 0;
    }
    .warning-box {
        background-color: #fff9e6;
        border-left: 4px solid #FFC107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 4px 4px 0;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
    }
    table th {
        background-color: #0066CC;
        color: white;
        text-align: left;
        padding: 8px;
    }
    table td {
        border: 1px solid #e0e0e0;
        padding: 8px;
    }
    table tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    /* Finland flag colors as accents */
    .fi-blue {
        color: #0066CC;
    }
    .fi-white {
        color: #FFFFFF;
    }
    .quick-action-card {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 3px solid #0066CC;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .quick-action-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .card-title {
        font-weight: bold;
        color: #0066CC;
        margin-bottom: 0.5rem;
    }
    .card-icon {
        float: right;
        font-size: 1.5rem;
        color: #0066CC;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "gpt-4.1-2025-04-14"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chat_started' not in st.session_state:
    st.session_state.chat_started = False
if 'greeting_added' not in st.session_state:
    st.session_state.greeting_added = False
if 'followup_questions' not in st.session_state:
    st.session_state.followup_questions = []
if 'followup_key' not in st.session_state:
    st.session_state.followup_key = 0
if 'pending_followup' not in st.session_state:
    st.session_state.pending_followup = None
if 'last_assistant' not in st.session_state:
    st.session_state.last_assistant = None

# Finnish Business Assistant system prompt
FINNISH_BUSINESS_ASSISTANT_PROMPT = """
You are a Finnish Business Planning Assistant, a specialized advisor helping users explore, evaluate, and refine business ideas tailored for the Finnish market. Your primary goal is to guide users through the business ideation, planning, testing, and market exploration process with focus on real-world applicability, theoretical grounding, and strategic foresight within Finland's unique business ecosystem.

🌐 Knowledge Base & Expertise:
• Possess comprehensive knowledge of Finnish business regulations (Companies Act, Business Income Tax Act, VAT legislation)
• Understand Finnish business culture, including decision-making approaches, work-life balance expectations, and negotiation styles
• Stay informed on Finnish economic conditions, including regional development differences across Helsinki, Tampere, Oulu, and other areas
• Recognize key Finnish business organizations (Business Finland, Finnvera, ELY Centers, TE Offices) and their roles
• Maintain awareness of EU-level regulations affecting Finnish businesses
• Track seasonal business considerations unique to Finland's climate and cultural calendar
• Understand Finnish sustainability standards and green business expectations

🛠️ Capabilities:
• Search the internet in real-time to provide up-to-date and Finland-relevant insights
• Guide on starting a business in Finland, including legal formalities, profitability, and growth areas
• Offer sector-specific trends with particular expertise in Finland's key industries:
  ○ Technology and ICT
  ○ Forestry and bioeconomy
  ○ Clean technology and circular economy
  ○ Tourism and hospitality
  ○ Health technology and wellbeing
• Facilitate brainstorming, business model generation, and idea validation
• Present frameworks such as SWOT, PESTEL, Lean Canvas, and Porter's Five Forces in a digestible format
• Break down business and entrepreneurship principles, tips, and strategies clearly
• Remain industry-agnostic by default, but pivot to specific industries on request
• Generate simple financial projections and break-even analyses tailored to Finnish market conditions
• Provide multilingual support in English, Finnish, and Swedish for key business terminology

🗣️ Tone & Style:
• Be insightful, structured, and actionable
• Use simple and clear language to make business concepts understandable
• Incorporate visual elements like:
  ○ Tables for comparative analyses
  ○ Flowcharts for processes
  ○ Icons (📌 🔍 ✅ ❗ 💡) for emphasis
  ○ Bullet points for clarity
• Encourage strategic thinking, backed by Finland-specific examples and models
• Balance comprehensive information with concise delivery
• Use a professional but approachable tone reflecting Finnish business culture's blend of formality and directness

📊 Response Structure:
• For complex responses, use a tiered approach:
  ○ Executive summary (2-3 sentences)
  ○ Key points (3-5 bullet points)
  ○ Detailed explanation (structured with headers)
  ○ Next steps or recommendations
• When presenting options, clearly mark pros and cons for the Finnish context
• Include citation links to official Finnish resources when referencing regulations or statistics
• For technical concepts, provide both theoretical explanation and practical application in Finland

🔄 Interaction Design:
• After each response:
  ○ Offer 2-3 relevant follow-up questions based on user context
  ○ Suggest a next logical step in the business planning process
  ○ Mention an additional relevant resource (e.g., "Business Finland offers grants for this sector")
• For information gaps:
  ○ Acknowledge limitations clearly
  ○ Offer to search for current information
  ○ Suggest alternative approaches or expert consultation
• For feedback loops:
  ○ Periodically ask if guidance is helpful and relevant
  ○ Adjust level of detail based on user expertise
  ○ Offer to refocus if conversation drifts from core business planning

🔒 Limitations & Error Handling:
• If asked about specific tax calculations or legal advice: "While I can provide general information about Finnish business taxation and regulations, for specific calculations or legal advice, I recommend consulting with a Finnish tax advisor or business lawyer. Would you like me to explain the general principles involved instead?"
• For requests outside business planning scope: "That falls outside my expertise as a Finnish business planning assistant. I'd be happy to redirect our conversation to areas where I can provide valuable guidance, such as [relevant alternatives]."
• For outdated information: "My knowledge about Finnish regulations may not reflect the most recent changes. Let me search for current information, or you might want to verify this with [appropriate Finnish authority]."
• For highly specialized industry questions: "This requires specialized industry knowledge. I can provide general business planning guidance, but for industry-specific details, consulting with [relevant Finnish industry association] would be beneficial."

🔐 Data Privacy & Ethics:
• Adhere to Finnish and EU data protection standards (GDPR)
• Never request or store personal or proprietary business information
• Provide disclaimers when discussing sensitive business matters
• Maintain neutrality when discussing competing Finnish businesses or platforms
• Respect intellectual property and encourage proper licensing in Finnish context

🔄 Information Currency:
• Indicate when information might be subject to change (especially tax rates, subsidies)
• Suggest verification with official sources for time-sensitive decisions
• Explicitly state when searching for current information
• Acknowledge regional variations within Finland when relevant

First Greeting: "Hei! I'm your Finnish Business Planning Assistant. I'm here to support your entrepreneurial journey in Finland with market insights, planning tools, and strategic guidance. To get started:
1. What type of business are you considering?
2. Are you familiar with the Finnish business environment?
3. What specific help do you need today—ideation, validation, planning, or market research?

I can provide information about startup requirements, funding options, business models, or industry trends specific to Finland."
"""

# Function to convert chat history to markdown format
def get_chat_history_markdown():
    """
    Convert the chat history to a markdown string format
    """
    markdown_text = "# Finnish Business Assistant Chat History\n\n"
    markdown_text += f"Session ID: {st.session_state.session_id}\n"
    markdown_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    markdown_text += f"Model: {st.session_state.selected_model}\n\n"
    markdown_text += "---\n\n"
    
    for message in st.session_state.chat_history:
        timestamp = message.get("timestamp", "")
        if message["role"] == "user":
            markdown_text += f"## User ({timestamp})\n\n"
            markdown_text += f"{message['content']}\n\n"
        else:
            markdown_text += f"## Assistant ({timestamp})\n\n"
            markdown_text += f"{message['content']}\n\n"
        markdown_text += "---\n\n"
    
    return markdown_text

# Function to process user questions
def process_question(question):
    """
    Process a question (typed or follow-up):
      1. Append as a user message.
      2. Run the LLM and stream the assistant's response.
    """
    # 1) Add user question to the chat
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.chat_history.append({
        "role": "user", 
        "content": question, 
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Set chat as started
    st.session_state.chat_started = True
    
    # 2) Get AI response
    start_time = time.time()
    
    if st.session_state.selected_model == "gpt-4.1-2025-04-14":
        response = call_openai_api(st.session_state.messages)
    else:
        response = call_langchain_anthropic_api(st.session_state.messages)
    
    # 3) Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": response, 
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # 4) Update follow-up tracking
    st.session_state.followup_key += 1
    
    # Store this as the latest assistant message for follow-up generation
    st.session_state.last_assistant = response

# Function to call OpenAI API using LangChain's ChatOpenAI
def call_openai_api(messages):
    try:
        # Initialize the LangChain OpenAI client
        chat = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-4.1-2025-04-14",
            max_tokens = 8000,
            streaming=True
        )
        
        # Format messages for OpenAI including system prompt and full chat history
        formatted_messages = [{"role": "system", "content": FINNISH_BUSINESS_ASSISTANT_PROMPT}]
        
        # Add conversation history
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Set up placeholder for streaming
        placeholder = st.empty()
        collected_content = ""
        
        # Process streaming response
        for chunk in chat.stream(formatted_messages):
            if chunk.content:
                collected_content += chunk.content
                # Apply reference styling
                styled_response = re.sub(
                    r'\[(.*?)\]',
                    r'<span class="reference">[\1]</span>',
                    collected_content
                )
                placeholder.markdown(f"""
                <div class="chat-message assistant">
                    <div class="avatar">🇫🇮</div>
                    <div class="message">{styled_response}</div>
                </div>
                """, unsafe_allow_html=True)
        
        return collected_content
    
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return "I'm sorry, there was an error processing your request. Please try again."

# Function to call Anthropic API using LangChain's ChatAnthropic (updated implementation)
def call_langchain_anthropic_api(messages):
    try:
        # Initialize the LangChain Anthropic client
        chat = ChatAnthropic(
            anthropic_api_key=ANTHROPIC_API_KEY,
            model="claude-3-7-sonnet-20250219",
            max_tokens = 8000
            )
        
        # Format messages for Anthropic
        formatted_messages = []
        
        # Add system message as first message
        formatted_messages.append({"role": "system", "content": FINNISH_BUSINESS_ASSISTANT_PROMPT})
        
        # Then add the conversation history
        for msg in messages:
            role = "human" if msg["role"] == "user" else "assistant"
            formatted_messages.append({"role": role, "content": msg["content"]})
        
        # Set up placeholder for streaming
        placeholder = st.empty()
        collected_content = ""
        
        # Process streaming response
        for chunk in chat.stream(formatted_messages):
            if hasattr(chunk, 'content') and chunk.content:
                collected_content += chunk.content
                # Apply reference styling
                styled_response = re.sub(
                    r'\[(.*?)\]',
                    r'<span class="reference">[\1]</span>',
                    collected_content
                )
                placeholder.markdown(f"""
                <div class="chat-message assistant">
                    <div class="avatar">🇫🇮</div>
                    <div class="message">{styled_response}</div>
                </div>
                """, unsafe_allow_html=True)
        
        return collected_content
    
    except Exception as e:
        st.error(f"Error calling Anthropic API: {str(e)}")
        return "I'm sorry, there was an error processing your request. Please try again."

# Function to handle follow-up question selection
def handle_followup(question):
    st.session_state.pending_followup = question

# Sidebar
with st.sidebar:
    st.markdown("<h1 class='sidebar-title'>🇫🇮 Finnish Business Assistant</h1>", unsafe_allow_html=True)
    
    st.markdown("### Select AI Model")
    
    # Model buttons with consistent sizing
    st.markdown("<div class='model-buttons'>", unsafe_allow_html=True)
    
    # OpenAI GPT-4o option
    openai_selected = st.session_state.selected_model == "gpt-4.1-2025-04-14"
    if st.button(
        f"OpenAI GPT-4o", 
        key="openai-btn", 
        help="OpenAI's GPT-4o model - versatile, high performance AI",
        type="secondary" if not openai_selected else "primary",
        use_container_width=True):
        st.session_state.selected_model = "gpt-4.1-2025-04-14"
        st.rerun()

    # Anthropic Claude option
    claude_selected = st.session_state.selected_model == "claude-3.7-sonnet"
    if st.button(
        f"Anthropic Claude 3.7-sonnet", 
        key="claude-btn", 
        help="Anthropic's Claude 3.7 Sonnet - excellent for structured business planning",
        type="secondary" if not claude_selected else "primary",
        use_container_width=True):
        st.session_state.selected_model = "claude-3.7-sonnet"
        st.rerun()


    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display selected model
    st.markdown(f"**Current Model:** {st.session_state.selected_model}")
    
    # Session controls
    st.markdown("### Session Controls")
    
    st.markdown("<div class='model-buttons'>", unsafe_allow_html=True)
    if st.button("🔄 Reset Conversation", key="new_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.chat_started = False
        st.session_state.greeting_added = False
        st.session_state.followup_questions = []
        st.session_state.last_assistant = None
        st.session_state.pending_followup = None
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    if st.button("📝 Export Chat History", key="export_chat", use_container_width=True):
        # Generate markdown format
        markdown_text = get_chat_history_markdown()
        # Encode to download
        b64 = base64.b64encode(markdown_text.encode()).decode()
        file_name = f"finnish_business_assistant_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        href = f'<a href="data:text/markdown;base64,{b64}" download="{file_name}">Click to download chat history (Markdown)</a>'
        st.markdown(href, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Industry quick references
    st.markdown("### Industries in Finland")
    st.markdown("""
    <div class="info-box">
        <p>🔹 <strong>Technology & ICT</strong> - Finland's tech hub</p>
        <p>🔹 <strong>Forestry & Bioeconomy</strong> - Traditional strength</p>
        <p>🔹 <strong>Cleantech</strong> - Growing circular economy</p>
        <p>🔹 <strong>Tourism & Hospitality</strong> - Seasonal opportunities</p>
        <p>🔹 <strong>Health Technology</strong> - Innovation leader</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key organizations
    st.markdown("### Key Organizations")
    st.markdown("""
    <div class="tip-box">
        <p>🔸 <strong>Business Finland</strong> - Funding, networks</p>
        <p>🔸 <strong>Finnvera</strong> - Loans, guarantees</p>
        <p>🔸 <strong>ELY Centers</strong> - Regional development</p>
        <p>🔸 <strong>TE Offices</strong> - Employment services</p>
        <p>🔸 <strong>PRH</strong> - Registration authority</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Business resources
    st.markdown("### Business Resources")
    st.markdown("""
    <div class="warning-box">
        <p>📚 <strong>Enterprise Finland</strong> - Information portal</p>
        <p>📚 <strong>Finnish Tax Administration</strong> - Tax guidance</p>
        <p>📚 <strong>Finnish Patent and Registration Office</strong> - Business registration</p>
        <p>📚 <strong>Chamber of Commerce</strong> - Business networking</p>
    </div>
    """, unsafe_allow_html=True)

# Main content
# Welcome card - ALWAYS show at the top regardless of chat status
st.title("🇫🇮 Finnish Business Assistant")
st.markdown("""
<div class="welcome-card">
    <div class="welcome-header">
        <div class="welcome-icon">🇫🇮</div>
        <h2>Welcome to Finnish Business Assistant</h2>
    </div>
    <div style="display: flex; gap: 20px; margin-bottom: 20px;">
        <div style="flex: 1; background-color: #f4f9ff; padding: 15px; border-radius: 8px; border-top: 3px solid #0066CC;">
            <h3 style="margin-top: 0; color: #0066CC;">Business Planning</h3>
            <ul style="padding-left: 20px; margin-bottom: 0;">
                <li>Market entry strategies</li>
                <li>Business models for Finland</li>
                <li>Financial projections</li>
                <li>SWOT & PESTEL analysis</li>
            </ul>
        </div>
        <div style="flex: 1; background-color: #f4f9ff; padding: 15px; border-radius: 8px; border-top: 3px solid #0066CC;">
            <h3 style="margin-top: 0; color: #0066CC;">Regulatory Guidance</h3>
            <ul style="padding-left: 20px; margin-bottom: 0;">
                <li>Legal business structures</li>
                <li>Taxation requirements</li>
                <li>Licensing information</li>
                <li>Employment regulations</li>
            </ul>
        </div>
        <div style="flex: 1; background-color: #f4f9ff; padding: 15px; border-radius: 8px; border-top: 3px solid #0066CC;">
            <h3 style="margin-top: 0; color: #0066CC;">Business Support</h3>
            <ul style="padding-left: 20px; margin-bottom: 0;">
                <li>Funding opportunities</li>
                <li>Networking resources</li>
                <li>Key organization contacts</li>
                <li>Industry-specific guidance</li>
            </ul>
        </div>
    </div>
    <div style="text-align: left; font-size: 16px; margin-top: 10px; line-height: 1.6;">
        <p style="margin-bottom: 10px;">I'm your specialized advisor for exploring and developing business ideas for the Finnish market. I can provide insights on:</p>
        <ul style="list-style-type: none; padding-left: 0;">
            <li>📌 <strong>Business planning and idea validation</strong> tailored to Finland's unique ecosystem</li>
            <li>📌 <strong>Regulatory guidance</strong> on Finnish and EU business requirements</li>
            <li>📌 <strong>Market insights</strong> for key Finnish industries and regions</li>
            <li>📌 <strong>Funding options</strong> through Business Finland, Finnvera, and other organizations</li>
        </ul>
        <p style="margin-top: 15px; font-weight: bold;">To get started, tell me about your business idea or what specific information you need about entrepreneurship in Finland.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick action cards using Streamlit components
st.markdown("### Quick Start Topics")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background-color: white; border-radius: 10px; padding: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 3px solid #0066CC; height: 160px;">
        <h3 style="color: #0066CC; margin-top: 0;">📝 Business Registration</h3>
        <p>Learn about the process and requirements for registering your business in Finland</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Explore Business Registration", key="card1"):
        handle_followup("What are the steps to register a business in Finland?")
        st.rerun()

with col2:
    st.markdown("""
    <div style="background-color: white; border-radius: 10px; padding: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 3px solid #0066CC; height: 160px;">
        <h3 style="color: #0066CC; margin-top: 0;">💰 Funding Options</h3>
        <p>Discover grants, loans, and investment opportunities for Finnish businesses</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Explore Funding Options", key="card2"):
        handle_followup("What funding options are available for startups in Finland?")
        st.rerun()

with col3:
    st.markdown("""
    <div style="background-color: white; border-radius: 10px; padding: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 3px solid #0066CC; height: 160px;">
        <h3 style="color: #0066CC; margin-top: 0;">📊 Business Plan Template</h3>
        <p>Get a customized business plan framework for the Finnish market</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Create Business Plan", key="card3"):
        handle_followup("Create a business plan template for a Finnish startup")
        st.rerun()

# Process a Pending Follow-Up (if any)
if st.session_state.pending_followup is not None:
    question = st.session_state.pending_followup
    st.session_state.pending_followup = None
    process_question(question)
    st.rerun()

# Display chat messages
if st.session_state.messages:
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                # Process the response to add styling to references
                styled_response = re.sub(
                    r'\[(.*?)\]',
                    r'<span class="reference">[\1]</span>',
                    message['content']
                )
                st.markdown(
                    f"**Assistant:** {styled_response}",
                    unsafe_allow_html=True
                )

# Chat input with prompt examples
user_input = st.chat_input("Ask about business planning, regulations, funding options, etc.")

# Quick prompt examples - using Streamlit's native functionality
st.markdown("### Quick Questions:")
col1, col2 = st.columns(2)

with col1:
    if st.button("How do I register a limited liability company (Oy) in Finland?", key="q1"):
        handle_followup("How do I register a limited liability company (Oy) in Finland?")
        st.rerun()
    
    if st.button("Explain the VAT requirements for a small business in Finland", key="q3"):
        handle_followup("Explain the VAT requirements for a small business in Finland")
        st.rerun()

with col2:
    if st.button("What funding options are available for tech startups in Finland?", key="q2"):
        handle_followup("What funding options are available for tech startups in Finland?")
        st.rerun()
    
    if st.button("What are the best cities to start a business in Finland?", key="q4"):
        handle_followup("What are the best cities to start a business in Finland?")
        st.rerun()

if user_input:
    # Add greeting if it's the first message and hasn't been added yet
    if len(st.session_state.messages) == 0 and not st.session_state.greeting_added:
        # Add system greeting with the starting question
        greeting = "Hei! I'm your Finnish Business Planning Assistant. I'm here to support your entrepreneurial journey in Finland with market insights, planning tools, and strategic guidance. To get started:\n\n1. What type of business are you considering?\n2. Are you familiar with the Finnish business environment?\n3. What specific help do you need today—ideation, validation, planning, or market research?\n\nI can provide information about startup requirements, funding options, business models, or industry trends specific to Finland."
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": greeting, 
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.session_state.greeting_added = True
    
    # Process the user's question
    process_question(user_input)
    st.rerun()