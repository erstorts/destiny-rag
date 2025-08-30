from openai import OpenAI
import segment.analytics as analytics
import os
from load_dotenv import load_dotenv

load_dotenv()

analytics.write_key = os.getenv("SEGMENT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def prompt_llm(search_results, user_input, num_results):
    return """given this data: '{}'
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

def response_llm(input_messages, message_counter):
    system_prompt = """You are a helpful librarian's assistant for middle school students.
    You are able to make suggestions about the library catalog, the books in the library, and the authors of the books.
    If you are asked questions that are not related to the library, the library catalog, the books in the library, or the authors of the books, you should say 
    'I'm sorry, I can only answer questions about the library, please try again.'"""
    response = client.responses.create(model="gpt-4o-mini", input=input_messages, instructions=system_prompt)
    msg = response.output_text
    analytics.track('null', event="assistant_response", properties={"assistant_response": msg, "message_counter": message_counter})

    return msg