import modules
import os
import shutil
from pathlib import Path
import chromadb
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from openai import OpenAI


load_dotenv()


input_repo= " "
#input_repo= "/Users/renee/Documents"
RESUME_DIR = Path(input_repo)
EMBEDDING_MODEL = "text-embedding-3-large"          # 3072 dims
  #directory fro DB, add the DB required for retreival. 
COLLECTION = f"resumes_{EMBEDDING_MODEL}"           # model-tied collection for insert/delete and search the resume data



#instantiating the OpenAIEmbeddings() class by calling the constructor of the class OpenAIEmbeddings()
emb = OpenAIEmbeddings(model=EMBEDDING_MODEL)
#instantiating the OpenAI() class by calling the constructor of the class OpenAI()
client = OpenAI()





# ---------- To load Documents ----------
#Below function, the argument 'folder' is of type 'Path'
def load_all_pdfs(folder: Path):
    docs = [] #empty list created
    for pdf in sorted(folder.glob("*.pdf")):
        for d in PyMuPDFLoader(str(pdf)).load():
            #loading each document ('d'), metadata, and appending to 'docs' list
            d.metadata = dict(d.metadata or {})
            d.metadata["source"] = str(pdf)
            #appneding each pdf to the "docs" list
            docs.append(d)
    return docs


#It is to chunk the documents using the RecursiveCharacterTextSplitter
def chunk_documents(docs, chunk_size=1000, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs) #retruning chunked docs, as a list

def store_embeddings_in_chroma(chunks):
    #remove the chromaDB from the Chroma path, if it exist. Basically clearing the ChromaDB collection.
    #shutil.rmtree(CHROMA_PATH, ignore_errors=True)
    # creates brand new collection tied to the current model
    vs = Chroma.from_documents(
        documents=chunks,
        embedding=emb,
        #persist_directory= #<Will have to add the DB directory> 
    )
    vs.persist()
    return vs

def retrieve_chunks(query, vectorstore, top_k=40):
    #Run similarity search with Chroma; returns list
    results = vectorstore.similarity_search(query, k=top_k * 2)
    unique_chunks = set() # This set will be created to have only unique chunks that came out of the similarity search and no duplicate chunks.
    uniq =  []
    for d in results:
        if d.page_content not in unique_chunks:
            uniq.append(d); unique_chunks.add(d.page_content)
        if len(uniq) >= top_k: break
    return uniq

def generate_answer(query, top_chunks):
    context = "\n\n".join(
        f"[SOURCE: {d.metadata.get('source','?')}] {d.page_content}"
        for d in top_chunks
    )
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    dev = "Respond with infromation from the document/s given to you. Do not retrieve data from the internet or hallucinate. "
    resp = client.chat.completions.create(
        #model needs to be flexible based on user's decision of LLM
        messages=[{"role":"developer","content":dev},
                  {"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content

# ---------- Data Ingestion (Loading the documents infromation ----------
def resume_agent(user_query: str, pdf_path: Path ):
    #Data Ingestion starts.
    raw_docs = load_all_pdfs(pdf_path)
    if not raw_docs:
        raise FileNotFoundError(f"No PDFs found in {pdf_path}")
    chunks = chunk_documents(raw_docs)
    #Storing the PDF's in ChromaDb as embeddings.
    vectordb = store_embeddings_in_chroma(chunks)
    # Data Ingestion ends.

    #This is retrieving the chunks based on the user prompt
    top = retrieve_chunks(user_query, vectordb)
    return generate_answer(user_query, top)


#----Get User input-----
def get_input():
    input_repo = input("Type the location where the documents are residing; ex. /Users/Repo/Documents ")
    user_prompt = input("Enter the prompt: ")
    return input_repo, user_prompt

##used for fast API
def trigger_agent(user_prompt, pdf_path):
    #pdf_path, user_prompt= get_input()
    dir= Path(pdf_path)
    dev1 = "Respond with meaningful format."
    response = resume_agent(f"{dev1}\n\n {user_prompt}", dir)
    return response



# ---------- Trigger the entire agent, localy in the terminal ----------
# if __name__ == "__main__":
#    input_repo = input("Type the location where the documents are residing; ex. /Users/Repo/Documents ")#     RESUME_DIR = Path(input_repo)
#     user_prompt= input("Enter the prompt: ")
#     dev1 = "Respond with meaningful format."
#     print()
#     print(response)



