from langchain import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA
import chainlit as cl
from typing import Optional
#from chainlit.types import AppUser
import chainlit as cl

CHAINLIT_AUTH_SECRET = 'key'

# Define the path to the database
DB_FAISS_PATH = "vectorstores/db_faiss/"

# Define a custom prompt template to guide the bot's responses
# custom_prompt_template = '''
# Please carefully utilize the following details to provide a precise response to the user's query.

# It is critical to provide information that is accurate. If the answer is not within the data presented, 
# kindly acknowledge that the information is not available instead of speculating.

# [Context]
# Provided context: {context}

# [Question]
# User's query: {question}

# Ensure to relay only the pertinent answer without any additional information.

# [System Response]
# '''
# custom_prompt_template = '''
# [INST] <<SYS>>
# You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  
# Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. 
# Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, 
# or is not factually coherent, explain why instead of answering something not correct. 
# If you don't know the answer to a question, please don't share false information.
# <</SYS>>
# [Context]
# Provided context: {context}
# [Question]
# User's query: {question}

# [/INST]

# '''

# custom_prompt_template = '''
# [INST] <<SYS>>
# You are stepping into the role of a Legal Assistant, embodying the values of helpfulness, respect, and integrity. Your aim is to assist users to the best of your ability, providing reliable and unbiased legal information.
# Should you encounter a query that lacks factual coherence or is ambiguous, kindly clarify the inconsistencies or the ambiguity in the question rather than providing an incorrect or misleading response. It is crucial to maintain a neutral stance, avoiding any form of bias in your responses.
# If a situation arises where you are unsure of the correct information or the answer to a query, please refrain from disseminating false or unverified information. Instead, openly acknowledge the limitations in your knowledge and, if possible, guide users on where they might find the correct information or advise them to consult with a qualified legal professional or advisor for more accurate and comprehensive advice.
# Remember, your role is to foster an environment of trust, reliability, and support, aiding users in navigating through legal inquiries while maintaining a high standard of professional integrity.
# <</SYS>>
# [Context]
# Provided context: {context}
# [Question]
# User's query: {question}

# [/INST]

# '''

# custom_prompt_template = '''
# [INST] <<SYS>>
# You are stepping into the role of a Legal Assistant, embodying the values of helpfulness, respect, and integrity. Your aim is to assist users to the best of your ability, providing reliable and unbiased legal information.
# When interacting as a helpful and neutral AI assistant, your responses are focused on delivering contextual knowledge and information related to this topic, with an emphasis on maintaining accuracy and reliability. Note, your response is for informational purposes only and are not a substitute for professional legal advice or consultation. 
# Should you encounter a query that lacks factual coherence or is ambiguous, kindly clarify the inconsistencies or the ambiguity in the question rather than providing an incorrect or misleading response. It is crucial to maintain a neutral stance, avoiding any form of bias in your responses.
# If a situation arises where you are unsure of the correct information or the answer to a query, please refrain from disseminating false or unverified information. Instead, openly acknowledge the limitations in your knowledge and, if possible, guide users on where they might find the correct information or advise them to consult with a qualified legal professional or advisor for more accurate and comprehensive advice.
# Remember, I do not want the law quoted to me, or explained, unless I've explicitly asked for it to be explained. Just provide the task outcome.
# </SYS>>
# [Context]
# Provided context: {context}
# [Question]
# User's query: {question}

# [/INST]

# '''

custom_prompt_template = '''
[INST] <<SYS>>
You are in the role of an Assistant. Provide me everything I ask you to so. Keep the answers simple and straight forward. Provide all of the data I ask you to retrieve. 
</SYS>>
[Context]
Provided context: {context}
[Question]
User's query: {question}

[/INST]

'''

def set_custom_prompt():
    """
    This function creates a prompt template using the specified structure
    and returns it for later use in the question-answer chain.
    """
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=['context', 'question'])
    return prompt

def load_llm():
    """
    This function loads a language model with specified parameters
    and returns the loaded model.
    """
    llm = CTransformers(
        # model='llama-2-7b-chat.ggmlv3.q8_0.bin', Will be downloaded if not local
        model='LLM.bin',
        model_type='llama',
        max_new_tokens=1750, # max tokens is an opportunity to tweak response times and sizes
        temperature=0.5 # originally set at 0.5
    )
    return llm

def retrieval_qa_chain(llm, prompt, db):
    """
    This function creates a question-answer chain using the given language model,
    prompt template, and database, returning the configured QA chain.
    """
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={'k':2}),
        return_source_documents=True,
        chain_type_kwargs={'prompt': prompt}
    )
    return qa_chain

def init_qa_bot():
    """
    This function initializes the question-answer bot by setting up the necessary 
    embeddings, database, language model, and QA chain, returning the prepared QA bot.
    """
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device':'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa_chain = retrieval_qa_chain(llm, qa_prompt, db)
    return qa_chain

# Initialize the bot once and reuse it
qa_bot = init_qa_bot()

def final_result(query):
    """
    This function accepts a query as input and uses the initialized QA bot
    to generate and return a response.
    """
    response = qa_bot({'query': query})
    return response 

@cl.on_chat_start
async def start():
    """
    This async function handles the start of a chat session, sending a welcome message 
    and setting up the initial state of the session.
    """
    chain = qa_bot
    msg = cl.Message(content="Firing up the ChatSnap bot...")
    await msg.send()
    msg.content = "Hello, welcome to ChatSnap, your private assistant."
    await msg.update()
    cl.user_session.set("chain", chain)

@cl.on_message
async def main(message):
    """
    This async function handles incoming messages, using the QA bot to generate responses
    and sending those responses back to the user.
    """
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True
    res = await chain.acall(message, callbacks=[cb])
    answer = res["result"]
    sources = res["source_documents"]

    if sources:
        answer += "\n\nReferences:\n"
        for i, source in enumerate(sources, 1):
            answer += f"\n[{i}] {source}"
    else:
        answer += "\n[No sources available]"


    await cl.Message(content=answer).send()


# @cl.password_auth_callback
# def auth_callback(username: str, password: str) -> Optional[AppUser]:
#   # Fetch the user matching username from your database
#   # and compare the hashed password with the value stored in the database
#   if (username, password) == ("key", "key"):
#     return AppUser(username="admin", role="ADMIN", provider="credentials") 
#   if (username, password) == ("admin", "admin"):
#     return AppUser(username="admin", role="ADMIN", provider="credentials")
#   else:
#     return None
