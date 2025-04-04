import os
import pdfplumber
import pandas as pd

def extract_tables_from_pdf(pdf_path):
    """
    Extracts all tables from a single PDF file.
    """
    tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract all tables on the current page
            extracted_tables = page.extract_tables()
            
            for table in extracted_tables:
                if table:  # Ensure the table is not empty
                    df = pd.DataFrame(table, columns=None, )
                    tables.append(df)
                    
    return tables

def fix_table(df):

    
    

    for row_idx in range(len(df)):
        row = df.iloc[row_idx]
        last_valid_value = None
        
        # Process each cell in the row
        for col_idx in range(len(row)):
            if pd.isna(row[col_idx]) or row[col_idx] is None:
                if last_valid_value is not None:
                    df.iloc[row_idx, col_idx] = last_valid_value
            else:
                last_valid_value = row[col_idx]
    df = df.ffill()
    try:
        for col in df.columns:
        # Skip the first two rows (header rows)
            if df[col].dtype == object:  # Check if column contains strings
                df[col] = df[col].apply(
                    lambda x: float(x.replace(" ", "")) if isinstance(x, str) and x.replace(" ", "").replace(".", "").isdigit() else x
                )
                df[col] = df[col].apply(
                    lambda x: str(x.replace("\n", " ")) if isinstance(x, str) else x
                )
    except:
        return df

    return df

def process_pdfs_in_directory(from_dir, to_dir):
    """
    Processes all PDFs in a directory, extracts tables, cleans them,
    and saves the results to CSV and Excel files.
    """
    for filename in os.listdir(from_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(from_dir, filename)
            md_path = os.path.join(to_dir, filename).replace(".pdf",".md")
            # print(f"Processing {filename}...")
            process_pdf(pdf_path, md_path)



def process_pdf(pdf_path, md_path):
    text = get_text(pdf_path)

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            markdown_output = ""
            # Extract tables from the page
            tables = page.extract_tables()

            # Process each table and append its Markdown representation
            for table in tables:
                # Convert the table to a DataFrame
                df = pd.DataFrame(table)  # Use the first row as headers
                
                # Clean the DataFrame using fix_table()
                cleaned_df = fix_table(df)
                
                # Convert the cleaned DataFrame to Markdown
                markdown_table = cleaned_df.to_markdown(index=False)
                
                # Append the Markdown table to the output
                markdown_output += markdown_table + "\n\n"
            text = text.replace(f"{{{page.page_number-1}}}------------------------------------------------",f"{page.page_number-1}------------------------------------------------\n\n{markdown_output}")
    with open(md_path, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"Processed PDF saved as '{md_path}'.")




            
def get_text(pdf_path):
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser
    from marker.output import text_from_rendered
    import re

    config = {
        "disable_image_extraction": True,
        "paginate_output": True,
        "output_format": "markdown",
        # "use_llm": True,
        # "llm_service": "marker.services.ollama.OllamaService",
        # "ollama_model": "deepseek-r1:70b"
    }
    config_parser = ConfigParser(config)
    converter = PdfConverter(
        artifact_dict=create_model_dict(),
        config=config_parser.generate_config_dict(),
        # llm_service=config_parser.get_llm_service()
    )
    # Parse the PDF into Markdown
    rendered = converter(pdf_path)
    text, _, _ = text_from_rendered(rendered)
    text = re.sub(r"^(\|[^\n]+\|\r?\n)((?:\|:?[-]+:?)+\|)(\n(?:\|[^\n]+\|\r?\n?)*)?$", "", text, flags=re.MULTILINE)
    return text
        



if __name__ == "__main__":
    # Specify the directory containing the PDF files
    from_dir = "pdf"
    to_dir = "markdown"
    # Process all PDFs in the directory
    process_pdfs_in_directory(from_dir, to_dir)

    print("All PDFs processed successfully!")