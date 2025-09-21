# Copyright (c) 2025 Robinson Fuller Ltd
# Licensed under the MIT License.

from tabulate import tabulate
from pyvis.network import Network


def visualise_output(
    papers,
    central_label="Search Results",
    output_file="visualized_results.html",
    use_similarity=False,
    base_length=50,
    scale=200,
    open_browser=True,
) -> None:
    """
    Visualizes paper search results using PyVis.

    Parameters:
        papers (list[dict]): Each dict should have "Filename", "Title", "Year", "DOI".
                             If `use_similarity` is True, it should also have "Similarity" (float in [0,1]).
        central_label (str): Label for the central node.
        output_file (str): Output HTML file name.
        use_similarity (bool): Whether to use similarity-based edge lengths.
        base_length (float): Base edge length (used if `use_similarity` is True).
        scale (float): Additional length scale for lower similarity.
    """
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

    net.add_node(
        central_label, label=central_label, title="Search root", size=30, color="red"
    )

    for idx, paper in enumerate(papers, start=1):
        title = paper.get("Title", "No title")
        doi = paper.get("DOI", "No DOI")
        author = paper.get("Author", "No author")
        similarity = float(paper.get("Similarity", 0.5)) if use_similarity else None

        node_id = f"paper_{idx}"
        node_title = f"Title: {title}<br>DOI: {doi}"
        if use_similarity and similarity is not None:
            node_title += f"<br>Similarity: {similarity:.2f}"

        url = None
        if doi and doi != "No DOI":
            url = doi if doi.startswith("http") else f"https://doi.org/{doi}"

        net.add_node(
            node_id,
            label=title,
            title=node_title,
            size=20,
            shape="dot",
            color="#97C2FC",
            link=url,
        )

        edge_length = (
            base_length + (1.0 - similarity) * scale
            if use_similarity and similarity is not None
            else None
        )
        net.add_edge(central_label, node_id, length=edge_length)

    net.write_html(output_file, open_browser=open_browser, notebook=False)


class Visualisation:
    """
    Handles the visualisation of paper data.

    Methods:
        list_papers(papers): Displays a table of papers with their rank and title.
    """

    def __init__(self):
        """
        Initializes the visualisation object.
        """
        pass

    def list_papers(self, papers) -> None:
        """
        Prints a formatted list of papers.

        Args:
            papers (list): A list of papers, each containing rank and title.

        Returns:
            None: Prints the paper list in a table format.
        """

        output = tabulate(papers, tablefmt="heavy_grid", headers=["Rank", "Title"])

        print(output)
