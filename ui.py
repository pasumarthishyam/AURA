import streamlit as st
import asyncio
import os
from dotenv import load_dotenv

# Import components
from core_controller import CoreAgentController, AgentState
from brain.brain import Brain
from tools.executor import Executor
from perception.voice import VoiceEngine
from memory.memory_system import MemorySystem
from safety.safety import Safety

# Load env
load_dotenv()

# Page Config
st.set_page_config(
    page_title="JARVIS-Lite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for "Jarvis" feel
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #00ffcc;
    }
    .stTextInput > div > div > input {
        color: #00ffcc;
    }
    .css-1d391kg {
        background-color: #111;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "agent" not in st.session_state:
    st.session_state.agent = None
    st.session_state.voice_enabled = False
    st.session_state.messages = []

def init_agent():
    """
    Initialize the Agent stack.
    """
    with st.spinner("Initializing JARVIS Protocols..."):
        # 1. Brain
        brain = Brain()
        
        # 2. Tools
        executor = Executor()
        
        # 3. Perception
        # Note: VoiceEngine loads model on GPU, might take a moment.
        perception = VoiceEngine()
        
        # 4. Memory & Safety (Mocking standard implementations if missing or using defaults)
        # Using placeholder classes if they don't fully exist/match yet in provided context, 
        # but based on file list they exist.
        # We need to ensure MemorySystem and SafetyChecker are instantiated correctly.
        # Assuming defaults work.
        memory = MemorySystem() 
        safety = Safety() # Using Safety module
        
        # 5. Core Controller
        controller = CoreAgentController(
            brain=brain,
            executor=executor,
            perception=perception,
            memory=memory,
            safety=safety
        )
        
        st.session_state.agent = controller
        st.success("JARVIS Online.")

# Sidebar
with st.sidebar:
    st.title("JARVIS Controls")
    if not st.session_state.agent:
        if st.button("Initialize System"):
            init_agent()
    else:
        st.success("System Operational")
        
    st.session_state.voice_enabled = st.checkbox("Voice Output", value=True)
    
    st.divider()
    st.write("System Stats:")
    st.write(f"GPU: NVIDIA RTX 3050 (Active)")

# Main Interface
st.title("JARVIS-Lite Interface")

# Chat Container
chat_container = st.container()

# Input
if st.session_state.agent:
    user_input = st.chat_input("Command JARVIS...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Run Agent
        with st.status("Processing...", expanded=True) as status:
            st.write("Thinking...")
            
            # Run the agent synchronously?
            # streamline run() is blocking. Ideally we run in thread or async.
            # For simplicity: blocking.
            
            result = st.session_state.agent.run(user_input)
            
            if result.success:
                status.update(label="Task Completed", state="complete")
            else:
                status.update(label="Task Failed", state="error")
                
            # Internal thought trace
            # In a real app we'd stream this. 
            # Controller stores trace.
            
            response = result.message
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Voice Output
            if st.session_state.voice_enabled:
                st.session_state.agent.perception.speak(response)

# Display Chat
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
if not st.session_state.agent:
    st.info("Please initialize the system from the sidebar.")
