def get_embedding(text, normalize=True):
    print("generating embeddings")
    from sentence_transformers import SentenceTransformer
    import numpy as np
    embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    is_list = isinstance(text, list)
    embeddings = embedding_model.encode(text)
    if normalize:
        if is_list:
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        else:
            embeddings = embeddings / np.linalg.norm(embeddings)
    return embeddings


def createDataset(documents):
    embeddings = get_embedding(documents["text"], normalize=True)
    documents['embeddings'] = embeddings.tolist()
    print("saving embeddings to documents-with-embeddings.pkl")
    documents.to_pickle("documents-with-embeddings.pkl")
    return documents

def createChunks():
    import os
    import json
    import re
    
    # List to store all document chunks
    documents = []
    
    # Counter for chunks within each file
    file_chunk_counter = {}
    
    # Page marker pattern
    page_pattern = re.compile(r'(\d+)------------------------------------------------')
    
    # Iterate through each file in the markdown folder
    for markdown_file in os.listdir("markdown"):
        print(markdown_file)
        
        catalog_name = markdown_file.replace(".md","")
        
        # Initialize chunk counter for this file
        file_chunk_counter[catalog_name] = 0
        
        # Read the markdown file content
        with open("markdown/"+markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content by page markers
        pages = page_pattern.split(content)
        
        # Process each page
        # Skip first element as it's empty text before the first marker
        for i in range(1, len(pages), 2):
            page_number = pages[i]  # This is the page number
            page_content = pages[i+1].strip()  # This is the page content
            
            # Skip empty pages
            if not page_content:
                continue
            
            # Look for main headers in the page content
            header_pattern = re.compile(r'^#\s+(.+?)$|^\*\*(.+?)\*\*$', re.MULTILINE)
            headers = header_pattern.findall(page_content)
            
            # Extract header (use first found header, or default if none found)
            page_header = "No Title"
            for h1, h2 in headers:
                if h1 or h2:
                    page_header = (h1 or h2).strip()
                    break
            
            # Create the chunk
            chunk_text = f"# {page_header}\n\n{page_content}"
            
            documents.append({
                "title": f"{catalog_name} - {page_number}",
                "text": chunk_text
            })
            file_chunk_counter[catalog_name] += 1
    
    # Write the documents to a JSON file
    with open("documents.json", 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    
    print(f"Created {len(documents)} chunks")
    return documents

def loadDocuments():
    import pandas as pd
    print("reading documents.json")
    return pd.read_json("documents.json")

def loadDocumentsWithEmbeddings():
    import pandas as pd
    print("reading documents-with-embeddings.pkl")
    return pd.read_pickle("documents-with-embeddings.pkl")

if __name__ == "__main__":
    # Create chunks from markdown files
    createChunks()
    # get load documents
    # Create dataset with embeddings
    documents = loadDocuments()
    createDataset(documents)

