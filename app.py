import streamlit as st
import requests
import io
import time
import base64
from streamlit_mic_recorder import mic_recorder

# Replace this URL with the one you copied from your n8n Webhook node
N8N_WEBHOOK_URL = "https://riyabhurse99.app.n8n.cloud/webhook-test/26cd6f01-275d-421a-a248-5078087cb6b2"

st.title("🗣️ AI Conversation Echo & Memory Reminder")
st.markdown("Record your thoughts or a conversation to extract tasks.")

# --- User Settings Section ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Email collection ONLY
    user_email = st.text_input(
        "📧 Your Email (for reminders)",
        placeholder="your.email@gmail.com",
        help="We'll send your daily task reminders to this email"
    )
    
    # Save settings button
    if st.button("💾 Save Settings"):
        if user_email:
            st.session_state.user_email = user_email
            st.success("✅ Settings saved!")
        else:
            st.error("❌ Please enter your email address")
    
    # Show current settings
    if 'user_email' in st.session_state:
        st.success(f"📧 Email: {st.session_state.user_email}")

# Check if email is configured
email_configured = 'user_email' in st.session_state and st.session_state.user_email

if not email_configured:
    st.warning("⚠️ Please configure your email in the sidebar to receive task reminders!")

# --- Quick Test Section (for debugging) ---
with st.expander("🔧 Quick Tests (for debugging)"):
    col1, col2, col3 = st.columns(3)  # Changed to 3 columns
    
    with col1:
        if st.button("Test Webhook Connection"):
            try:
                test_data = {"test": "connection"}
                response = requests.post(N8N_WEBHOOK_URL, json=test_data, timeout=10)
                st.write(f"Status: {response.status_code}")
                if response.status_code == 200:
                    st.success("✅ Webhook works!")
                else:
                    st.error(f"❌ Status {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
    
    with col2:
        if st.button("🎤 Test with Local Audio + Email"):
            try:
                # Load the local audio file
                with open("/home/riya/Desktop/Aham.ai/audio.wav", 'rb') as f:
                    audio_data = f.read()
                
                # Prepare files and data (same as main recording)
                files = {
                    'audio': ('audio.wav', io.BytesIO(audio_data), 'audio/wav')
                }
                
                data = {
                    'user_email': st.session_state.get('user_email', 'test@example.com')
                }
                
                # Show what we're sending
                st.write("🔍 **Debug Info:**")
                st.write(f"Audio size: {len(audio_data)} bytes")
                st.write(f"User email: {data['user_email']}")
                
                # Send the request
                response = requests.post(
                    N8N_WEBHOOK_URL, 
                    files=files,
                    data=data,
                    timeout=120
                )
                
                st.write(f"**Status**: {response.status_code}")
                
                if response.status_code == 200:
                    st.success("✅ Local audio + email test works!")
                    
                    # Show the response
                    try:
                        result = response.json()
                        
                        # Display results nicely (same as main section)
                        if isinstance(result, dict):
                            # Look for transcription
                            if 'transcription' in result:
                                st.subheader("📝 Transcription:")
                                st.write(result['transcription'])
                            
                            # Look for tasks
                            if 'tasks' in result:
                                st.subheader("✅ Extracted Tasks:")
                                tasks = result['tasks']
                                if isinstance(tasks, list) and len(tasks) > 0:
                                    for i, task in enumerate(tasks, 1):
                                        if isinstance(task, dict):
                                            st.write(f"**{i}.** {task.get('task_description', 'Unknown task')}")
                                            if task.get('time_date') != 'Not specified':
                                                st.write(f"   📅 Due: {task.get('time_date')}")
                                            st.write(f"   🚨 Priority: {task.get('priority', 'Medium')}")
                                            st.write(f"   📧 User: {task.get('user_email', 'Not provided')}")
                                            st.write("---")
                                else:
                                    st.info("No specific tasks detected.")
                            
                            # Show full response
                            with st.expander("📋 Full Response Details"):
                                st.json(result)
                        else:
                            st.write("**Response:**")
                            st.write(result)
                            
                    except Exception as json_error:
                        st.success("✅ **Audio processed successfully!**")
                        st.write("**Raw Response:**")
                        st.code(response.text[:1000])
                else:
                    st.error(f"❌ Failed: {response.status_code}")
                    st.code(response.text[:500])
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    # NEW: Add this third column
    with col3:
        if st.button("📧 Test Email Reminders"):
            try:
                # Updated with your correct Workflow 2 webhook URL
                WORKFLOW_2_URL = "https://riyabhurse99.app.n8n.cloud/webhook-test/test-reminders"
                
                st.info("🔄 Triggering reminder workflow...")
                
                response = requests.get(WORKFLOW_2_URL, timeout=30)
                
                if response.status_code == 200:
                    st.success("✅ Reminder workflow triggered successfully!")
                    st.info("📧 Check your email for task reminders!")
                    
                    # Show response if available
                    try:
                        result = response.json()
                        st.write("**Workflow Result:**")
                        st.json(result)
                    except:
                        st.write("**Raw Response:**")
                        st.code(response.text[:500])
                        
                else:
                    st.error(f"❌ Workflow failed: {response.status_code}")
                    st.code(response.text[:300])
                    
            except Exception as e:
                st.error(f"❌ Error triggering reminders: {e}")

st.divider()

# --- Main Recording Section ---
st.header("🎤 Record Your Conversation")

# Initialize session state for the recorder
if 'audio_processed' not in st.session_state:
    st.session_state.audio_processed = False

# Single mic recorder
audio_data = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹️ Stop Recording", 
    just_once=False,  # Allow multiple recordings
    use_container_width=True,
    key="main_recorder"
)

# Process the recorded audio
if audio_data is not None and audio_data.get('bytes') is not None:
    
    # Get the audio bytes
    audio_bytes = audio_data['bytes']
    
    # Show audio player
    st.audio(audio_bytes, format='audio/wav')
    
    # Show audio info
    st.info(f"📊 Recorded {len(audio_bytes)} bytes of audio")
    
    # ADD THIS NEW SECTION FOR TASK GUIDANCE
    with st.expander("💡 Improve Task Detection"):
        st.markdown("""
        **For better task extraction, try saying:**
        - "I need to call John tomorrow at 2 PM"
        - "Remember to buy groceries this evening"
        - "Don't forget to email the report by Friday"
        - "I should schedule a doctor's appointment"
        - "I have to finish the presentation before Monday"
        
        **Include specific times when possible:**
        - "Call mom at 5 PM today"
        - "Meeting with Sarah on Wednesday at 10 AM"
        - "Submit assignment by next Friday"
        """)
    
    # Validate audio size
    if len(audio_bytes) < 2000:  # Increased minimum size
        st.warning("⚠️ Audio seems very short. Try recording for at least 3-5 seconds with clear speech.")
    else:
        st.success("✅ Audio recorded successfully!")
        
        # Process button
        if st.button("🚀 Process with AI", use_container_width=True, type="primary"):
            
            with st.spinner("🧠 Processing your audio with AI..."):
                try:
                    # Prepare the audio file for sending
                    audio_file = io.BytesIO(audio_bytes)

                    files = {
                        'audio': ('recording.wav', audio_file, 'audio/wav')
                    }

                    data = {
                        'user_email': st.session_state.get('user_email', 'not_provided')
                    }

                    response = requests.post(
                        N8N_WEBHOOK_URL, 
                        files=files,
                        data=data,
                        timeout=120
                    )
                    
                    # DEBUG: Show the actual response from n8n
                    st.write("🔍 **n8n Response Debug:**")
                    st.write(f"Status: {response.status_code}")
                    st.write(f"Response text: {response.text[:500]}")
                    
                    # Handle the response
                    if response.status_code == 200:
                        st.success("✅ **Successfully processed your conversation!**")
                        
                        if email_configured:
                            st.info(f"📧 Task reminders will be sent to: {st.session_state.user_email}")
                        
                        try:
                            result = response.json()
                            
                            # Display results nicely
                            if isinstance(result, dict):
                                # Look for transcription
                                if 'transcription' in result:
                                    st.subheader("📝 Transcription:")
                                    st.write(result['transcription'])
                                
                                # Look for tasks
                                if 'tasks' in result:
                                    st.subheader("✅ Extracted Tasks:")
                                    tasks = result['tasks']
                                    if isinstance(tasks, list) and len(tasks) > 0:
                                        for i, task in enumerate(tasks, 1):
                                            if isinstance(task, dict):
                                                st.write(f"**{i}.** {task.get('task_description', 'Unknown task')}")
                                                if task.get('time_date') != 'Not specified':
                                                    st.write(f"   📅 Due: {task.get('time_date')}")
                                                st.write(f"   🚨 Priority: {task.get('priority', 'Medium')}")
                                                st.write("---")
                                    else:
                                        st.info("No specific tasks detected in this conversation.")
                                
                                # Show full response in expander
                                with st.expander("📋 Full Response Details"):
                                    st.json(result)
                            else:
                                st.write("**Response:**")
                                st.write(result)
                                
                        except Exception as json_error:
                            st.success("✅ **Audio processed successfully!**")
                            st.write("**Response:**")
                            response_text = response.text
                            if len(response_text) > 500:
                                st.text_area("Response", response_text, height=200)
                            else:
                                st.write(response_text)
                    
                    else:
                        st.error(f"❌ **Processing failed** (Status: {response.status_code})")
                        st.write("**Error details:**")
                        st.code(response.text[:1000] + "..." if len(response.text) > 1000 else response.text)
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ **Request timed out.** The AI processing is taking longer than expected. Please try again.")
                    
                except requests.exceptions.ConnectionError:
                    st.error("🔌 **Connection error.** Please check your internet connection.")
                    
                except Exception as e:
                    st.error(f"❌ **Unexpected error:** {str(e)}")
                    
        # Add some helpful tips
        st.markdown("""
        ---
        ### 💡 **Tips for better results:**
        - Speak clearly and at a normal pace
        - Mention specific dates/times for better task scheduling
        - Use phrases like "I need to...", "Remember to...", "Don't forget to..."
        - Record in a quiet environment
        """)

else:
    st.info("👆 Click the microphone button above to start recording your conversation.")
    
# Footer
st.markdown("""
---
*Your conversations are processed securely and tasks are automatically saved for reminders.*
""")