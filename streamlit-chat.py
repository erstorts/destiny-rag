import streamlit as st
import segment.analytics as analytics
import requests

analytics.write_key = st.secrets["SEGMENT_API_KEY"]


st.sidebar.title("Select the number of results to return")
num_results = st.sidebar.slider("Number of results", min_value=1, max_value=10, value=3)


st.title("💬 Whitman Middle School Library Catalog Chat")
st.caption("Ask me for book suggestions!")

if "display_messages" not in st.session_state:
    st.session_state["display_messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "message_counter" not in st.session_state:
    st.session_state["message_counter"] = 1

for msg in st.session_state.display_messages:
    st.chat_message(msg["role"]).write(msg["content"])
if user_input := st.chat_input():

    # Add user's actual question to display messages
    st.session_state.display_messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    analytics.track('null',event="user_input", properties={"user_input": user_input, "message_counter": st.session_state.message_counter})
    
    # Add full prompt with search results to context messages for the model
    with st.status("Thinking..."):
        response = requests.get("http://localhost:8000/llm", json={"user_input": user_input, 
                                                                     "num_results": num_results, 
                                                                     "message_counter": st.session_state.message_counter,
                                                                     "input_messages": st.session_state.display_messages})
        msg = response.json()

    # Add assistant response to both display and context messages
    st.session_state.display_messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").markdown(msg)
    st.session_state.message_counter += 1
    print(st.session_state.message_counter)