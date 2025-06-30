import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from google import genai
from google.genai import types
from langchain.chains import ConversationalRetrievalChain
import pinecone
from langchain import hub
from langchain_core.output_parsers import StrOutputParser  # Import the StrOutputParser class for parsing the output of the language model
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain.chains import create_history_aware_retriever  # Import the create_history_aware_retriever function
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain  # Import the create_retrieval_chain function from the langchain.chains module
from langchain.chains.combine_documents import create_stuff_documents_chain  # Import the ChatPromptTemplate and MessagesPlaceholder classes
from langchain_core.messages import HumanMessage
from app.config import Config
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
#vectorstore = PineconeVectorStore.from_documents(texts, embeddings, index_name=os.environ.get("INDEX_NAME"))

try:
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=Config.INDEX_NAME,
        embedding=embeddings # Pass the embedding model used for the index
    )
    print(f"Successfully connected to Pinecone index: {Config.INDEX_NAME}!")
except Exception as e:
    print(f"An error occurred while connecting to Pinecone: {e}")
    print("Please ensure:")
    print("1. Your .env file has correct PINECONE_API_KEY, PINECONE_ENVIRONMENT, and INDEX_NAME.")
    print("2. The Pinecone index (named in INDEX_NAME) actually exists in your Pinecone console.")
    print("3. The 'embeddings' object (model and dimensionality) matches what was used to create the index.")
    exit() # Exit if we can't connect to the vectorstore

retriever = vectorstore.as_retriever(
    search_type="similarity",  # Specify the search type as "similarity" for vector similarity search
    search_kwargs={"k": 3}  # Set the number of top results to retrieve (k=3)
)
chat_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001", # Using a powerful and fast Gemini model
    temperature=0,               # Set to 0 for more deterministic, factual answers
    verbose=True                 # Enable verbose output to see chain execution details
)
def format_docs(docs):
    """
    Format a list of documents by joining their page_content with newline separators.
    Args:
        docs (list): A list of document objects.
    Returns:
        str: A string containing the concatenated page_content of all documents, separated by newlines.
    """
    return "\n\n".join(doc.page_content for doc in docs)# Define the Retrieval-Augmented Generation (RAG) chain

template = """Use the following pieces of context to answer the question at the end.
Also change language if user asked
If you don't know the answer, just say that Please say go to Contact section and mail us.
Use three sentences maximum and keep the answer as concise as possible.
Always say "thanks for asking!" at the end of the answer.
You are a chatbot for Power Blue International Company. When there is link try sending link that will work.
Dont say anything abot context
{context}  # This placeholder will be replaced with the retrieved context (relevant documents)

Question: {question}  # This placeholder will be replaced with the user's question

Helpful Answer:"""  # This is the prompt for the language model to generate a helpful answer

# Create a PromptTemplate instance from the template string
custom_rag_prompt = PromptTemplate.from_template(template)

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""

# Create a ChatPromptTemplate for contextualizing the question
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),  # Set the system prompt
        MessagesPlaceholder("chat_history"),  # Placeholder for the chat history
        ("human", "{input}"),  # Placeholder for the user's input question
    ]
)
history_aware_retriever = create_history_aware_retriever(
    chat_gemini,  # Pass the language model instance
    retriever,  # Pass the retriever instance
    contextualize_q_prompt  # Pass the prompt for contextualizing the question
)
# Define the system prompt for the question-answering task
qa_system_prompt = """You are an assistant for Power blue company. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, Please say contact us at powerblueindia@gmail.com for further assistance. \
Always Greet the user before answering the question and say thank you at the end.
Use three sentences maximum and keep the answer concise.\

{context}"""  # This placeholder will be replaced with the retrieved context

# Create a ChatPromptTemplate for the question-answering task
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),  # Set the system prompt
        MessagesPlaceholder("chat_history"),  # Placeholder for the chat history
        ("human", "{input}"),  # Placeholder for the user's input question
    ]
)
question_answer_chain = create_stuff_documents_chain(chat_gemini, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)