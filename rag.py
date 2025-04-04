import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from create_dataset import get_embedding, loadDocumentsWithEmbeddings
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"using {device}")
# Global variables to store model, tokenizer, and conversation history
model = None
tokenizer = None
conversation_history = []

def getModelAndTokenizer():
    """
    Initialize and return the model and tokenizer.
    This function ensures they are only loaded once.
    """
    global model, tokenizer
    
    if model is None or tokenizer is None:
        model_name = "Qwen/Qwen2.5-1.5B-Instruct"
        
        print(f"Loading model and tokenizer: {model_name}")
        model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    return model, tokenizer

def getRelevantContext(prompt):
    """
    Retrieve relevant context from the document database based on the prompt.
    """
    prompt_embedding = get_embedding(prompt)

    def getDistance(page_embedding):
        return np.dot(page_embedding, prompt_embedding)

    df = loadDocumentsWithEmbeddings()
    df['distance'] = df['embeddings'].apply(getDistance)

    df.sort_values('distance', ascending=False, inplace=True)

    # Combine top 5 most relevant chunks
    context = "\n\n".join(df['text'].iloc[:5].tolist())
    return context

def prediction(prompt, chat_history=None):
    """
    Generate a response based on the prompt and chat history.
    
    Args:
        prompt (str): The current user query
        chat_history (list, optional): List of previous messages in the conversation
    
    Returns:
        str: The model's response
    """
    global conversation_history
    
    # Initialize chat history if not provided
    if chat_history is None:
        chat_history = conversation_history
    
    # Get relevant context for the current prompt
    context = getRelevantContext(prompt)
    # print(context)
    # Create system message
    system_message = {"role": "system", "content": "You are an assistant who answers questions about HVAC from context given to you. Please answer as if you are talking to an engineer who has good understanding of details of HVAC."}
    
    # Add current prompt to messages
    user_message = {"role": "user", "content": prompt}

    # Create context message
    context_message = {"role": "assistant", "content": f"Find the answer to the user's question in the context and give it to them. If you cannot find the answer in the context, ask for more details from the user instead of using your own knowledge: {context}. Please strictly use the context provided and don't use your own information. Don't try making calculations only search for answer in context."}
    

    
    # Construct the full message list with history
    messages = [system_message]
    
    # Add conversation history if it exists
    if chat_history:
        messages.extend(chat_history)
    
    # Add the context and current user message
    messages.append(user_message)
    messages.append(context_message)
    
    # Get model and tokenizer
    model, tokenizer = getModelAndTokenizer()

    # Format the conversation for the model
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    # Generate response
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # Update conversation history
    conversation_history.append(user_message)
    conversation_history.append({"role": "assistant", "content": response})
    
    return response

def chat():
    """
    Interactive chat function that maintains conversation history.
    """
    global conversation_history
    
    print("HVAC Assistant Chat (type 'exit' to quit)")
    print("----------------------------------------")
    
    # Initialize model and tokenizer
    getModelAndTokenizer()
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nAssistant: Goodbye! Have a great day.")
            break
        
        response = prediction(user_input)
        print("\nAssistant: ", end="")
        print(response)

def reset_chat():
    """
    Reset the conversation history.
    """
    global conversation_history
    conversation_history = []
    print("Chat history has been reset.")

if __name__ == "__main__":
    # Example of single prediction
    # prompt = "What is the maximum heating capacity for a 40 ton MPS unit?"
    # output = prediction(prompt)
    # print(f"prompt: {prompt}\n\nresponse: {output}")
    
    # Interactive chat mode
    chat()

# https://www.youtube.com/watch?v=P8tOjiYEFqU


