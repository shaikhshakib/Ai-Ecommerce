import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

KNOWLEDGE_BASE = "knowledge_base"
CHROMA_PATH = "chroma_path"


def search_knowledge_base(query, k=3):
    embeddings = OpenAIEmbeddings(
        model = "text-embedding-3-small"
    )


    vectorstore = Chroma(
        collection_name = "celeste_rose_knowledge",
        embedding_function= embeddings,
        persist_directory=CHROMA_PATH
    )
    
    results = vectorstore.similarity_search(
        query,
        k=k
    )
    return results
def create_vector_database():
    documents = []

    for filename in os.listdir(KNOWLEDGE_BASE):

        if filename.endswith(".txt"):
            file_path = os.path.join(KNOWLEDGE_BASE, filename)

            with open(file_path, "r", encoding= "utf-8") as file:
                content = file.read()

            documents.append(
                Document(
                    page_content = content,
                    metadata = {"source" : filename}
                )
            )
        if not documents:
            print("No documents found in knowledge_base!")
            return
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 500,
            chunk_overlap = 50
        )

        chunks = text_splitter.split_documents(documents)

        embeddings = OpenAIEmbeddings(
            model = "text-embedding-3-small"
        )

        vectorstore = Chroma(
            collection_name="celeste_rose_knowledge",
            embedding_function=embeddings,
            persist_directory=CHROMA_PATH
        )

        chunk_ids = [
            f"{chunk.metadata['source']}_{index}"
            for index, chunk in enumerate(chunks)
        ]

        vectorstore.add_documents(
            documents = chunks,
            ids = chunk_ids
        )

        print("Documents successfully stored in ChromaDB")
        print("Total Chunks: ", len(chunks))



if __name__ == "__main__":

    results = search_knowledge_base(
        "How should I take care of my jewellery?"
    )

    for result in results:
        print("\nRetrieved Content:")
        print(result.page_content)

        print("Source:", result.metadata["source"])
