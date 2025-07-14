import faiss
import numpy as np
import os

embeddings_dir = 'data/processed/embeddings'
embedding_files = [f for f in os.listdir(embeddings_dir) if f.endswith('npy')]


all_embeddings = []
shot_names = []

for fname in embedding_files:
    emb = np.load(os.path.join(embeddings_dir, fname))
    # emb shape: (1, 512) or (512,)
    emb = emb.squeeze() # Ensure it's 1D
    all_embeddings.append(emb)
    shot_names.append(fname.replace('_embeddings.npy', ''))

all_embeddings = np.stack(all_embeddings).astype('float32')
# Normalize the embeddings
all_embeddings = all_embeddings / np.linalg.norm(all_embeddings, axis=1, keepdims=True)

# Build FAISS index
index = faiss.IndexFlatIP(512) # Using Inner Product for similarity
index.add(all_embeddings)

# Save index and shot names
faiss.write_index(index, 'db/faiss/faiss_clip.index')
np.save('db/faiss/shot_names.npy', np.array(shot_names))