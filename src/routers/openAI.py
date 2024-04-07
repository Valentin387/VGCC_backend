#Libraries
from http.client import HTTPResponse
from fastapi import HTTPException, APIRouter
import os
from dotenv import load_dotenv
import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.documents import Document
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from models.openAIModels import InputText

load_dotenv() 

# Load environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize ChatGPT instance
llm = ChatOpenAI(openai_api_key=api_key)

# Load content from the local file
def load_content():
  file_path = "text.txt"
  try:
    with open(file_path, "r", encoding="utf-8") as file:
      text_content = file.read()
  except FileNotFoundError:
    # If the file doesn't exist, create it with some initial content
    with open(file_path, "w", encoding="utf-8") as file:
      current_datetime = datetime.datetime.now()
      formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
      text_content = f"Current date and time: {formatted_datetime}\n"
      text_content = text_content + "Below are the fetched events from several google calendars' APIs"
      file.write(text_content)
  return text_content

text_content = load_content()

# the embeddings prepare the document for vectorization
embeddings = OpenAIEmbeddings(openai_api_key=api_key)

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents([Document(page_content=text_content)])
vector = FAISS.from_documents(documents, embeddings)

# First we need a prompt that we can pass into an LLM to generate this search query
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's questions based on the below context: \n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])

document_chain = create_stuff_documents_chain(llm, prompt)
retriever = vector.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)
#retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
#retrieval_chain = create_retrieval_chain(retriever_chain, document_chain)

chat_history = [HumanMessage(content="Hello"), AIMessage(content="Hello! how can I help you today?")]

# Initialize FastAPI router
openAI_router = APIRouter()

    
# Endpoint to receive user input and return LLM response
@openAI_router.post("/llm/response/", tags=["OpenAI"])
async def llm_response(input_text_data: InputText):
    # Get LLM response for user input
    input_text = input_text_data.input_text

    response = retrieval_chain.invoke({
    "chat_history": chat_history,
    "input": input_text
    })
    # Update chat history with the new human query and AI response
    chat_history.append(HumanMessage(content=input_text))
    chat_history.append(AIMessage(content=response["answer"]))

    return {"openAI response": response["answer"]}

# Endpoint to delete text.txt
@openAI_router.delete("/delete-text/", tags=["OpenAI"])
async def delete_text():
    try:
        os.remove("text.txt")
        return {"message": "text.txt deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="text.txt not found")
    
# Endpoint to create a new text.txt
@openAI_router.post("/create-text/", tags=["OpenAI"])
async def create_text():
    try:
        with open("text.txt", "w", encoding="utf-8") as file:
            file.write("Text file created successfully")
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            text_content = f"Current date and time: {formatted_datetime}\n"
            text_content = text_content + "Below are the fetched events from several google calendars' APIs"
            file.write(text_content)
        return {"message": "Text file created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   
    
# Endpoint to append text to text.txt
@openAI_router.post("/append-text/", tags=["OpenAI"])
async def try_append_text(text_to_append_data: InputText):
    text_to_append = text_to_append_data.input_text
    await append_text(text_to_append)  # No need to await the HTTPResponse
    return {"message": "Text appended successfully. Retrieval chain updated."}
    
    
async def append_text(text_to_append: str):
    try:
        with open("text.txt", "a", encoding="utf-8") as file:
            file.write(text_to_append + "\n")
        # Reload content and rebuild retrieval chain after appending
        global text_content, documents, vector, retrieval_chain
        text_content = load_content()  # Reload content after appending
        documents = text_splitter.split_documents([Document(page_content=text_content)])
        vector = FAISS.from_documents(documents, embeddings)
        retriever = vector.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        # # FastAPI handles 200 status for you
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
