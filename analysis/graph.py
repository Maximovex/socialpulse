import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from analysis.predictor import get_embeddings
import networkx as nx
import pandas as pd
from sqlalchemy import text
from storage.database import get_connection

def load_stories() -> pd.DataFrame:
    with get_connection() as conn:
        result = conn.execute(text("SELECT author, title, score FROM stories WHERE author IS NOT NULL"))
        return pd.DataFrame(result.fetchall(), columns=["author", "title", "score"])

def build_author_topic_graph() -> nx.Graph:
    df=load_stories()
    g = nx.Graph()

    # add authors as nodes
    for author in df["author"].unique():
        author_stories = df[df["author"] == author]
        g.add_node(author,
                   story_count=len(author_stories),
                   avg_score=author_stories["score"].mean())

    return g

def get_author_embedding(titles: list[str]) -> np.ndarray:
    """Average embeddings of all author's titles"""
    embeddings = get_embeddings(titles)  # reuse from predictor.py
    return embeddings.mean(axis=0)



def build_similarity_graph(threshold: float = 0.95) -> nx.Graph:
    with get_connection() as conn:
        result = conn.execute(text("""
            SELECT author, 
                   avg(embedding) as avg_embedding,
                   COUNT(*) as story_count,
                   AVG(score) as avg_score
            FROM stories
            WHERE embedding IS NOT NULL
            AND author IS NOT NULL
            GROUP BY author
            HAVING COUNT(*) > 1
        """))

        def parse_embedding(raw) -> np.ndarray:
            if isinstance(raw, np.ndarray):
                return raw
            if isinstance(raw, str):
                # remove brackets and split
                clean = raw.strip('[]')
                return np.array([float(x) for x in clean.split(',')])
            return np.array(raw)

        # generator — yields one row at a time
        def row_generator():
            for row in result:
                embedding=parse_embedding(row.avg_embedding)
                yield row.author, embedding, \
                    row.story_count, float(row.avg_score)

        authors, embeddings, story_counts, avg_scores = [], [], [], []
        for author, embedding, count, score in row_generator():
            authors.append(author)
            embeddings.append(embedding)
            story_counts.append(count)
            avg_scores.append(score)

    embeddings = np.array(embeddings)
    sim_matrix = cosine_similarity(embeddings)

    G = nx.Graph()
    for i, author in enumerate(authors):
        G.add_node(author, story_count=story_counts[i], avg_score=avg_scores[i])

    for i in range(len(authors)):
        for j in range(i + 1, len(authors)):
            if sim_matrix[i][j] > threshold:
                G.add_edge(authors[i], authors[j],
                           weight=float(sim_matrix[i][j]))

    return G

def visualising_graph(graph: nx.Graph):
    from pyvis.network import Network
    net = Network(height="800px", width="100%", notebook=False)
    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "stabilization": {"iterations": 200}
      }
    }
    """)
    net.from_nx(graph)
    net.write_html("graph.html")


if __name__ == "__main__":
    G = build_similarity_graph()

    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Connected components: {nx.number_connected_components(G)}")

    # degree centrality - who has most connections?
    centrality = nx.degree_centrality(G)
    top_authors = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"Most connected authors: {top_authors}")
    visualising_graph(G)
