from models.openAIModels import InputText
from fastapi import HTTPException
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.chains import create_retrieval_chain, create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
import os
import datetime

# Load environment variables
API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")  # Defaulting to a placeholder if not found

# Initialize ChatGPT and other services
llm = ChatOpenAI(openai_api_key=API_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)
text_splitter = RecursiveCharacterTextSplitter()

# Global variables to maintain state
text_content = None
documents = None
vector_store = None
retrieval_chain = None
chat_history = [HumanMessage(content="Hello"), AIMessage(content="Hello! How can I help you today?")]

# Load or initialize text content and set up retrieval chain
def initialize_text_content_and_chain():
    global text_content, documents, vector_store, retrieval_chain
    text_content = load_content("text.txt")
    documents = text_splitter.split_documents([Document(page_content=text_content)])
    vector_store = FAISS.from_documents(documents, embeddings)
    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's questions based on the below context: \n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])

    retrieval_chain = create_retrieval_chain(retriever, llm, prompt)

initialize_text_content_and_chain()

def load_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return create_initial_text(file_path)

def create_initial_text(file_path):
    current_datetime = datetime.datetime.now()
    initial_content = f"Current date and time: {current_datetime:%Y-%m-%d %H:%M:%S}\nBelow are the fetched events from several Google calendars' APIs\n"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(initial_content)
    return initial_content

async def get_llm_response(input_text_data: InputText):
    global chat_history
    input_text = input_text_data.input_text
    response = retrieval_chain.invoke({
        "chat_history": chat_history,
        "input": input_text
    })
    chat_history.append(HumanMessage(content=input_text))
    chat_history.append(AIMessage(content=response["answer"]))
    return {"response": response["answer"]}

async def handle_text_deletion():
    file_path = "text.txt"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="text.txt not found")
    os.remove(file_path)
    return {"message": "text.txt deleted successfully"}

async def handle_text_creation():
    text_content = create_initial_text("text.txt")
    initialize_text_content_and_chain()  # Re-initialize the chain with the new content
    return {"message": "Text file created successfully", "content": text_content}

async def handle_text_append(input_data: InputText):
    text_to_append = input_data.input_text
    with open("text.txt", "a", encoding="utf-8") as file:
        file.write(text_to_append + "\n")
    initialize_text_content_and_chain()  # Re-load and re-initialize after appending
    return {"message": "Text appended successfully. Retrieval chain updated."}

async def interpret_and_schedule_event(input_text_data: InputText):
    """
    Interprets natural language input to schedule a calendar event.
    Uses ChatGPT to extract event details from the input text.
    """
    # Ask ChatGPT to interpret the input text and extract event details
    prompt = f"Extract event details from the following input: {input_text_data.input_text}"
    chat_response = llm.generate(prompt)
    try:
        # Assuming the response is JSON-formatted event details
        event_details = json.loads(chat_response)
        event_data = EventCreateInput(**event_details)
        return await create_calendar_event(event_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Failed to interpret event details.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
