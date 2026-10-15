from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def compute_similarity(text1: str, text2: str) -> float:
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    similarity = util.cos_sim(embedding1, embedding2)
    return float(similarity[0][0])