import time
from openai import OpenAI
import streamlit as st
from pinecone import Pinecone

pc = Pinecone()
client = OpenAI()
index_name = "quickstart-py"
dense_index = pc.Index(index_name)

system_prompt = """You are a helpful librarian's assistant. 
You are able to answer questions about the library catalog and that is all."""

st.sidebar.title("Select the number of results to return")
num_results = st.sidebar.slider("Number of results", min_value=1, max_value=10, value=3)

def search_pinecone(query):
    reranked_results = dense_index.search(
        namespace="example-namespace",
        query={
            "top_k": num_results,
            "inputs": {
                'text': query
            }
        },
        rerank={
            "model": "bge-reranker-v2-m3",
            "top_n": num_results,
            "rank_fields": ["synopsis"]
        }   
    )

    return reranked_results['result']['hits']


st.title("💬 Whitman Middle School Library Catalog Chat")
st.caption("Ask me anything about the library catalog!")

if "display_messages" not in st.session_state:
    st.session_state["display_messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "context_messages" not in st.session_state:
    st.session_state["context_messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.display_messages:
    st.chat_message(msg["role"]).write(msg["content"])


if user_input := st.chat_input():

    search_results = search_pinecone(user_input)

    prompt = """given this data: '{}' and past context, 
    answer this question: '{}'.
    Format your response as Markdown, as a list of books, with the title, author, and a short summary.
    The title should be bolded.
    The author should be in italics.
    The summary should be in regular text.
    You response should include {} number of books.
    You should start your response with something like 'Here is the information I found: '""".format(search_results, user_input, num_results)


    # Add user's actual question to display messages
    st.session_state.display_messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    
    # Add full prompt with search results to context messages for the model
    st.session_state.context_messages.append({"role": "user", "content": prompt})
    with st.status("Thinking..."):
        response = client.responses.create(model="gpt-3.5-turbo", input=st.session_state.context_messages, instructions=system_prompt)
        msg = response.output_text
    
    # Add assistant response to both display and context messages
    st.session_state.display_messages.append({"role": "assistant", "content": msg})
    st.session_state.context_messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").markdown(msg)