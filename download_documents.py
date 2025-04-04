def download_pdfs():
    import os
    import requests
    os.makedirs("pdf", exist_ok=True)
    with open("pdf_links.txt", "r") as fp:
        for line in fp:
            url = line.strip()
            response = requests.get(url)
            filename = url.split("/")[-1]
            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"
            with open(os.path.join("pdf", filename), "wb") as pdf_file:
                pdf_file.write(response.content)

if __name__ == "__main__":
    # download_pdfs()
    pass
