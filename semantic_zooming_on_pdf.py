from langchain_community.document_loaders import PyPDFLoader
import json

# Open the PDF file in read-binary mode
pdf_doc = PyPDFLoader('./Social-origin-of-self-regulatory-competence.pdf').load()

for doc in pdf_doc:
    # print(doc.page_number)
    page_text = doc.page_content
    page_num = doc.metadata["page"]
    # Create a dictionary to store the page content
    page_content = {"page": page_num + 1, "content": page_text}
    # Write the page content to a JSON file
    with open(f'page{page_num + 1}.json', 'w') as json_file:
        json.dump(page_content, json_file)