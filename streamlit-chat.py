from openai import OpenAI
import streamlit as st
from pinecone import Pinecone
import segment.analytics as analytics
import json

analytics.write_key = st.secrets["SEGMENT_API_KEY"]
pc = Pinecone()
client = OpenAI()

analytics.send = True


system_prompt = """You are a helpful librarian's assistant for middle school students.
You are able to make suggestions about the library catalog, the books in the library, and the authors of the books.
If you are asked questions that are not related to the library, the library catalog, the books in the library, or the authors of the books, you should say 
'I'm sorry, I can only answer questions about the library, please try again.'"""

st.sidebar.title("Select the number of results to return")
num_results = st.sidebar.slider("Number of results", min_value=1, max_value=10, value=3)

def search_pinecone(query, index_type):

    if index_type == "dense":
        index_name = "whitman-dense"
    elif index_type == "sparse":
        index_name = "whitman-sparse"

    index = pc.Index(index_name)
    reranked_results = index.search(
        namespace=index_name,
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

    print(reranked_results)

    for hit in reranked_results['result']['hits']:
        hit_dict = hit.to_dict()
        json_hit = json.dumps(hit_dict)
        analytics.track('null', event="search_result", properties={"search_result": json_hit, "index_type": index_type})
    
    return reranked_results['result']['hits']


st.title("💬 Whitman Middle School Library Catalog Chat")
st.caption("Ask me for book suggestions!")

if "display_messages" not in st.session_state:
    st.session_state["display_messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "context_messages" not in st.session_state:
    st.session_state["context_messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.display_messages:
    st.chat_message(msg["role"]).write(msg["content"])

message_counter = 0
if user_input := st.chat_input():


    dense_search_results = search_pinecone(user_input, "dense")
    sparse_search_results = search_pinecone(user_input, "sparse")

    search_results = dense_search_results + sparse_search_results
    print(search_results)

    prompt = """given this data: '{}'
    --- 
    answer this question: '{}'.
    ---
    Remember, you are able to make suggestions about the library catalog, the books in the library, and the authors of the books.
    ---
    Format your response as a list of books, with the title, author, catalog url, and a short summary.
    The title should be bolded.
    The author should be in italics.
    The summary should be in regular text.
    The catalog url is https://wauwatosa.follettdestiny.com/portal/portal?app=Library%20Manager&appId=destiny-V34X-8FVV&siteGuid=7C1FFC98-98CC-4282-A8D9-8EBE432B86F9&nav=%252Fcataloging%252Fservlet%252Fpresenttitledetailform.do%253FsiteTypeID%253D-2%2526siteID%253D%2526includeLibrary%253Dtrue%2526includeMedia%253Dfalse%2526mediaSiteID%253D%2526bibID%253D[FILL IN HERE]
    with the 'FILL IN HERE' being where to put the bib_id from the answers.
    ---
    You response should include {} number of books.""".format(search_results, user_input, num_results)



    # Add user's actual question to display messages
    st.session_state.display_messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    analytics.track('null',event="user_input", properties={"user_input": user_input, "message_counter": message_counter})
    
    # Add full prompt with search results to context messages for the model
    st.session_state.context_messages.append({"role": "user", "content": prompt})
    with st.status("Thinking..."):
        response = client.responses.create(model="gpt-4o-mini", input=st.session_state.context_messages, instructions=system_prompt)
        msg = response.output_text
        analytics.track('null', event="assistant_response", properties={"assistant_response": msg, "message_counter": message_counter})
    
    # Add assistant response to both display and context messages
    st.session_state.display_messages.append({"role": "assistant", "content": msg})
    st.session_state.context_messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").markdown(msg)
    message_counter += 1