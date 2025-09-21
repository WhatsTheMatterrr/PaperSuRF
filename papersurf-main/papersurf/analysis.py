# Copyright (c) 2025 Robinson Fuller Ltd
# Licensed under the MIT License.

from sentence_transformers import SentenceTransformer
from keybert import KeyBERT

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

query_list_papers = """
    MATCH (p:Paper)
    OPTIONAL MATCH (a:Author)-[:WROTE]->(p)  // Optional match for authors
    RETURN COALESCE(a.name, 'No Author') AS Author, p.title AS Title, p.doi AS DOI, p.year AS Year  // Use COALESCE to handle papers with no authors
    ORDER BY p.year ASC
"""

query_search_by_title = """
    MATCH (p:Paper)
    WHERE toLower(p.title) CONTAINS toLower($title_val)
    OPTIONAL MATCH (a:Author)-[:WROTE]->(p)  // Optional match for authors
    RETURN p.title AS Title, COALESCE(a.name, 'No Author') AS Author, p.doi AS DOI, p.year AS Year  // Use COALESCE to handle papers with no authors
    ORDER BY p.year ASC
"""


query_search_by_author = """
    MATCH (a:Author)-[:WROTE]->(p:Paper)
    WHERE toLower(a.name) CONTAINS toLower($author_val)
    RETURN a.name AS Author, p.filename AS Filename, p.title AS Title, p.doi AS DOI, p.year AS Year
    ORDER BY p.year ASC
"""

query_search_by_topic = """
    MATCH (p:Paper)-[:HAS_TOPIC]->(t:Topic)
    WHERE toLower(t.name) CONTAINS toLower($topic_val)
    OPTIONAL MATCH (a:Author)-[:WROTE]->(p)  // Optional match for authors
    WITH p, t, a
    ORDER BY t.name 
    WITH p, collect(t.name) AS topicList, COALESCE(a.name, 'No Author') AS Author  // Collect topics and handle papers with no author
    RETURN p.filename AS Filename, p.title AS Title, Author, p.doi AS DOI, head(topicList) AS Topic, p.year AS Year
    ORDER BY p.year ASC
"""

query_search_by_semantic = """
    MATCH (p:Paper)
    WHERE p.embedding IS NOT NULL
    OPTIONAL MATCH (a:Author)-[:WROTE]->(p)  // Optional match for authors
    RETURN p.filename AS Filename, p.title AS Title, COALESCE(a.name, 'No Author') AS Author, p.year AS Year, p.embedding AS Embedding, p.doi AS DOI
"""


class Analysis:
    def __init__(self):
        """
        Initializes the Analysis class with a SentenceTransformer model for text embedding.

        Args:
            model (str, optional): The name or path of the SentenceTransformer model to use.
                                    Defaults to "all-MiniLM-L6-v2".

        Initializes the object for embedding text and preparing for similarity analysis.
        No return value.
        """

        # @NOTE: that the initialization of these libraries increases
        # startup time significantly. We need to find a way of optimising
        # this.

        self.model = "all-MiniLM-L6-v2"
        self.sentence_transformer = SentenceTransformer(model_name_or_path=self.model)
        self.keyword_extractor = KeyBERT(model=self.model)

    def find_papers_by_similarity(
        self, driver, query_text, top_n=15, threshold=0.2
    ) -> list[tuple]:
        """
        Finds and returns the top N papers most similar to a given query text.

        Args:
            driver: A Neo4j database driver/session used to run the semantic search query.
            query_text (str): The input query text to compare against stored paper embeddings.
            top_n (int, optional): The number of top similar papers to return. Defaults to 15.

        Returns:
            list[tuple]: A list of tuples, each containing:
                - Title (str)
                - Author (str)
                - DOI (str)
                - Similarity score (float)
            The list is sorted in descending order of similarity.
        """

        result = driver.run(query_search_by_semantic)
        query_vec = self.sentence_transformer.encode(query_text, convert_to_numpy=True)
        query_vec = query_vec.reshape(1, -1)

        # Calculate the cosine similarity of query and return papers
        papers = []
        for record in result:
            paper_embedding = record["Embedding"]
            if not paper_embedding:
                continue

            paper_vector = np.array(paper_embedding, dtype=np.float32).reshape(1, -1)
            paper_similarity = cosine_similarity(query_vec, paper_vector)[0][0]

            if paper_similarity < threshold:
                continue

            papers.append(
                [
                    record.get("Title", "Untitled"),
                    record.get("Author", "Unknown Author"),
                    record.get("DOI", "No DOI"),
                    paper_similarity,
                ]
            )

        # Sort by similarity and return the top_n results
        return sorted(papers, key=lambda x: x[3], reverse=True)[:top_n]
