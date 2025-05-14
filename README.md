# Custom RAG Model Project

One of my recent projects was a custom RAG model.  
This project required me to learn a lot of things about machine learning.

My older brother is an HVAC sales engineer and he wanted a chatbot that he could ask questions to that would be able to pull an answer from very complex PDFs about various HVAC models.  
I decided this problem would be best solved with a RAG model which I had only recently learned about.

While working on this project I learned about:
- Data chunking
- Embeddings
- How to find the most relevant data to a prompt  
  (Generate an embedding for the prompt and find the most similar embedding in the document embeddings → feed the top *n* most relevant pieces of context to a chat model to answer the prompt)

I also ran into issues when fine-tuning. A lot of the accuracy of RAG comes from organizing the chunks and properly parsing the PDFs, which was honestly the most difficult part of the project.

For any use case other than HVAC PDFs, using a PDF parsing library called **Marker** would be enough.  
But the tables in the HVAC PDFs were very complicated, and often Marker was unable to parse them correctly.  
I had to create a custom table parser and merge it with the rest of the parsed PDF.

Additionally, chunking the text and tables that were parsed is another huge factor for accuracy.  
It is recommended to **overlap chunks** so that their embeddings can be more similar.

Halfway through this project I slowly realized that maybe RAG wasn't the way to go, but I pushed through hoping that optimizations would make it work better.  
In the end, it didn't work as accurately as my brother required, but I still consider this project important for two reasons:
1. I learned a lot from it.
2. I can use this on more simple PDFs or scraped websites in the future.

---

## TL;DR

I built a custom RAG model for my brother, an HVAC sales engineer, to answer questions from complex HVAC PDFs.  
This involved learning about embeddings, chunking, and prompt-context matching.  
The biggest challenge was accurately parsing and chunking tables from the PDFs, which required a custom parser.  
While the final result wasn’t accurate enough for his needs, the project taught me a lot and laid the groundwork for future applications on simpler documents.
