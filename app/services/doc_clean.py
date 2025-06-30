import re
import unicodedata
from itertools import groupby

def clean_chunk(text):
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_document_splits_with_ids(docs):
    document_ids = []
    for page, chunks in groupby(docs, lambda chunk: chunk.metadata.get('page', 0)):
        for chunk_id, chunk in enumerate(chunks):
            file_name = chunk.metadata.get('source', 'unknown').split('/')[-1].replace(' ', '_')
            document_ids.append(f"{file_name}_page{page}_chunk{chunk_id}")
    return document_ids