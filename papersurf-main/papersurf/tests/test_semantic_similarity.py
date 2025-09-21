# © 2025 PaperSuRF. Licensed under the MIT License.
# Free to use, modify, and distribute without warranty.

# test_semantic_similarity.py
# This unit test verifies that the SentenceTransformer model, "all-MiniLM-L6-v2," generates
# a predictable similarity ranking among a predefined set of ten phrases.
# If the assertion fails, it indicates that the model version or weights might have changed
# and are no longer producing the expected ranking.

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

# Define 10 phrases, ID from 1 to 10
phrases = {
    1: "deep learning for natural language processing",
    2: "neural networks in text classification",
    3: "convolutional neural networks for image recognition",
    4: "transformers in NLP",
    5: "support vector machines for sentiment analysis",
    6: "recurrent neural networks in translation",
    7: "graph neural networks in recommendation systems",
    8: "transfer learning in BERT models",
    9: "unsupervised learning for topic modeling",
    10: "language models and pretraining",
}


def compute_similarity(text1, text2):
    emb1 = model.encode([text1], convert_to_numpy=True)
    emb2 = model.encode([text2], convert_to_numpy=True)
    return cosine_similarity(emb1, emb2)[0][0]


def test_phrase_similarity_ranking():
    query = phrases[1]  # ID 1 is the reference query
    results = []

    for idx, text in phrases.items():
        if idx == 1:
            continue
        sim = compute_similarity(query, text)
        results.append((idx, text, sim))

    # Sort by similarity descending
    results.sort(key=lambda x: x[2], reverse=True)

    print(f"\nQuery phrase (ID 1): {query}")
    print("\nRanked similarities:")
    for rank, (idx, text, sim) in enumerate(results, start=1):
        print(f"Rank {rank}: ID {idx} | Similarity: {sim:.4f} | Phrase: {text}")

    # Optional: assert expected ranking
    expected_rank_order = [2, 6, 3, 4, 9, 10, 5, 8, 7]
    actual_rank_order = [idx for idx, _, _ in results]
    assert (
        actual_rank_order == expected_rank_order
    ), f"The version of similarity model mismatch.\nExpected: {expected_rank_order}\nGot: {actual_rank_order}"
