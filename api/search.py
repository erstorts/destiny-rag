from pinecone import Pinecone
import segment.analytics as analytics
import json
import os

analytics.write_key = os.getenv("SEGMENT_API_KEY")
pc = Pinecone()

def search_pinecone(user_input, index_type, num_results, message_counter):

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
                'text': user_input
            }
        },
        rerank={
            "model": "bge-reranker-v2-m3",
            "top_n": num_results,
            "rank_fields": ["synopsis"]
        }   
    )

    for hit in reranked_results['result']['hits']:
        hit_dict = hit.to_dict()
        json_hit = json.dumps(hit_dict)
        analytics.track('null', event="search_result", properties={"search_result": json_hit, "index_type": index_type, "message_counter": message_counter})

    return reranked_results['result']['hits']


def search(user_input, num_results, message_counter):
    all_searched_results = []
    all_searched_results.append(search_pinecone(user_input, "sparse", num_results, message_counter))
    all_searched_results.append(search_pinecone(user_input, "dense", num_results, message_counter))
    return all_searched_results

