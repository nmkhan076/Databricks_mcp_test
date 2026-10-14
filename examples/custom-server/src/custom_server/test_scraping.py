from fda_rag import download_webpage

chunks = download_webpage()

print("Total chunks:", len(chunks))
print("First chunk:")
print(chunks[0]["text"][:500])