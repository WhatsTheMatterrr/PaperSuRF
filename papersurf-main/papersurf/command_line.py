# Copyright (c) 2025 Robinson Fuller Ltd
# Licensed under the MIT License.

import re
import os
import threading

from sklearn.metrics.pairwise import cosine_similarity

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.widgets import Label, TextArea, Frame
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import WindowAlign
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.buffer import Buffer

from tabulate import tabulate

from conf import settings
from paper import Paper
from analysis import *
from visualisation import visualise_output


welcome_message = r"""
    ____                        _____       ____  ____
   / __ \____ _____  ___  _____/ ___/__  __/ __ \/ __/
  / /_/ / __ `/ __ \/ _ \/ ___/\__ \/ / / / /_/ / /_  
 / ____/ /_/ / /_/ /  __/ /   ___/ / /_/ / _, _/ __/  
/_/    \____/ .___/\___/_/   /____/\____/_/ |_/_/     
           /_/                                        

Enter the 'help' command to view the main help menu.
        """


def papers_load(path, keyword_extractor, output_writer=None) -> list[Paper]:
    """
    Loads papers from the specified directory, extracts metadata, topics, and keyphrases.

    Args:
        path (str): The directory path containing the paper files.

    Returns:
        list[Paper]: A list of Paper objects that were successfully loaded and processed.

    This method loads each paper, extracts the DOI, topics (keywords), and the main keyphrase.
    If extraction fails, it handles exceptions and sets default values.
    """
    if output_writer is None:
        output_writer = print

    path = os.path.expanduser(path)

    if not os.path.exists(path):
        return []

    items = []
    for file_name in os.listdir(path):
        if not file_name.lower().endswith(".pdf"):
            output_writer(f"Error: {file_name} is not a PDF file. Skipping.")
            continue

        file_path = os.path.join(path, file_name)

        paper = Paper()
        output_writer(f"Phrasing file: {file_name}")
        if not paper.load(file_path):
            output_writer(f"Failed to load: {file_path}")
            continue

        # Extract DOI
        output_writer("Extracting DOI Link", "-------")
        # Simple DOI regularization
        doi_pattern = r"(?:doi:\s*)?(10\.\d{4,9}/[-._;()/:a-zA-Z0-9_]+)"
        match = re.search(doi_pattern, paper.text, flags=re.IGNORECASE)

        if match:
            doi_raw = match.group(1).rstrip(".,;()[]!?\"'")
            # Convert to clickable link and deduplication
            paper.doi = f"https://doi.org/{doi_raw}"
        if not match:
            match_meta = re.search(doi_pattern, paper.title, flags=re.IGNORECASE)
            if match_meta:
                doi_raw = match_meta.group(0).rstrip(".,;()[]!?\"'")
                # Convert to clickable link and deduplication
                paper.doi = f"https://doi.org/{doi_raw.replace('doi:', '').strip()}"
            else:
                paper.doi = "NO PROVIDED DOI"

        output_writer(f"DOI link extracted")
        output_writer(f"Extracting Topics", "---------")
        # Extract 5 keywords
        extracted_topics = keyword_extractor.extract_keywords(
            paper.text,
            top_n=5,
            keyphrase_ngram_range=(1, 7),
            stop_words=None,
            diversity=0.6,
        )
        if extracted_topics:
            paper.topics = [topic for topic, score in extracted_topics]
            paper.main_keyphrase = paper.topics[0]
        output_writer(f"Topics extracted")
        items.append(paper)

    return items


def add_paper(session, sentence_transformer, paper) -> None:
    """
    Stores a paper's data into the Neo4j database, including:
      - Creating or updating Paper, Author, and Topic nodes.
      - Establishing relationships:
        - (Author)-[:WROTE]->(Paper)
        - (Paper)-[:HAS_TOPIC]->(Topic)
      - Storing the paper's `embedding` and DOI in the Paper node.

    Args:
        session: The Neo4j session to execute database queries.
        paper (dict): A dictionary containing the paper's data (e.g., filename, title, authors, topics, DOI, etc.).

    Returns:
        None: This method performs database operations and does not return a value.
    """

    # Extract paper info from either a Paper object or a dictionary
    filename = paper.get("filename", "No filename")
    title = paper.get("title", "No title")
    year = paper.get("year", "No year")
    authors = paper.get("authors", ["No authors"])
    topics = paper.get("topics", ["No topics"])
    doi = paper.get("doi", "NO DOI")
    main_keyphrase = paper.get("main_keyphrase", "No keyphrase")

    embedding = sentence_transformer.encode(
        main_keyphrase, convert_to_numpy=True
    ).tolist()

    # Merge Paper node
    session.run(
        """
        MERGE (p:Paper {filename: $filename})
        ON CREATE SET p.title = $title,
                      p.year = $year,
                      p.embedding = $embedding, 
                      p.doi = $doi
        """,
        {
            "filename": filename,
            "title": title,
            "year": year,
            "embedding": embedding,
            "doi": doi,
        },
    )

    # Merge Author nodes and relationships
    for author in authors:
        session.run("MERGE (a:Author {name: $name})", {"name": author})
        session.run(
            """
            MATCH (p:Paper {filename: $filename}),
                (a:Author {name: $name})
            MERGE (a)-[:WROTE]->(p)
            """,
            {"filename": filename, "name": author},
        )

    # Merge Topic nodes and relationships
    for topic in topics:
        session.run("MERGE (t:Topic {name: $topic})", {"topic": topic})
        session.run(
            """
            MATCH (p:Paper {filename: $filename}),
                (t:Topic {name: $topic})
            MERGE (p)-[:HAS_TOPIC]->(t)
            """,
            {"filename": filename, "topic": topic},
        )


class CommandLineInterface:
    def __init__(self) -> None:
        self.running = True
        self.max_character_limit = 100

        # Word to function pointer mapping. This is used so that the command
        # handler knows which function to call.
        self.commands = {
            # Long verison of commands
            "exit": self.command_exit,
            "help": self.command_help,
            "list": self.command_list_papers,
            "search": self.command_search,
            "vsearch": self.command_search,
            "simsearch": self.command_search_by_similarity,
            "vsimsearch": self.command_search_by_vsemantic,
            "add": self.command_add_papers_by_users,
            # Shorthand version of commands
            "e": self.command_exit,
            "h": self.command_help,
            "lp": self.command_list_papers,
            "st": self.command_search,
            "sa": self.command_search,
            "sp": self.command_search,
            "ss": self.command_search_by_similarity,
            "vsh": self.command_search,
            "vss": self.command_search_by_vsemantic,
            "a": self.command_add_papers_by_users,
        }

    def run(self, analysis, driver_session) -> None:
        self.analysis = analysis
        self.session = driver_session

        # This is for query completion which will automatically handle search
        # completition based on this specified dictionary.
        self.command_completer = NestedCompleter.from_nested_dict(
            {
                "list": {"papers": None},
                "search": {
                    "title": None,
                    "author": None,
                    "topic": None,
                },
                "vsearch": {
                    "title": None,
                    "author": None,
                    "topic": None,
                },
                "simsearch": None,
                "vsimsearch": None,
                "exit": None,
                "add": None,
                "help": None,
            }
        )

        # Define the user interface layout for the command line
        self.input_field = TextArea(
            height=1,
            prompt="$ ",
            multiline=False,
            focus_on_click=False,
            accept_handler=self.command_handler,
            completer=self.command_completer,
            auto_suggest=AutoSuggestFromHistory(),
            history=InMemoryHistory(),
        )
        # Set function callback for when text changes to limit input
        self.input_field.buffer.on_text_changed += self.input_limit_length

        self.output_area = TextArea(
            text=welcome_message + "\n",
            wrap_lines=False,
            scrollbar=True,
            focusable=True,
            read_only=True,
            focus_on_click=False,
        )
        title_layout = HSplit(
            [
                VSplit(
                    [
                        Label(
                            "  ",
                            width=6,
                            align=WindowAlign.LEFT,
                            dont_extend_width=True,
                        ),
                        Window(
                            FormattedTextControl(
                                [
                                    (
                                        "fg:#87cefa bold",
                                        f"{settings.APPLICATION_NAME} (c)\n",
                                    ),
                                    (
                                        "fg:#b0b0b0",
                                        f"{settings.APPLICATION_DESCRIPTION}\n",
                                    ),
                                    ("fg:#b0b0b0", f"{settings.ORGANISATION}\n"),
                                ]
                            ),
                            align=WindowAlign.CENTER,
                        ),
                        Label(
                            f"{settings.APPLICATION_VERSION}",
                            width=6,
                            align=WindowAlign.RIGHT,
                            dont_extend_width=True,
                        ),
                    ]
                ),
            ]
        )

        self.layout = Layout(
            HSplit(
                [
                    title_layout,
                    Frame(self.input_field, title="Enter Command"),
                    Frame(self.output_area, title="Output"),
                ]
            )
        )

        self.bindings = KeyBindings()

        @self.bindings.add("c-c")
        def _(event):
            event.app.exit()

        @self.bindings.add("up")
        def _(event):
            self.output_scroll_up()

        @self.bindings.add("down")
        def _(event):
            self.output_scroll_down()

        @self.bindings.add("pageup")
        def _(event):
            self.output_scroll_up()

        @self.bindings.add("pagedown")
        def _(event):
            self.output_scroll_down()

        self.application = Application(
            layout=self.layout,
            full_screen=True,
            key_bindings=self.bindings,
            mouse_support=False,
        )
        self.application.run()

    def output_clear(self):
        self.output_area.text = ""

    def output_write(self, text, end="\n"):
        self.output_area.text += text + end

    def output_print(self, text, end="\n"):
        self.output_area.text += text + end
        self.application.invalidate()

    def output_scroll_up(self):
        self.output_area.window.vertical_scroll -= 1
        self.output_area.buffer.cursor_up(count=1)

    def output_scroll_down(self):
        self.output_area.window.vertical_scroll += 1
        self.output_area.buffer.cursor_down(count=1)

    def input_limit_length(self, buffer: Buffer) -> None:
        if len(buffer.text) > self.max_character_limit:
            buffer.text = buffer.text[: self.max_character_limit]

    def generate_table_str(self, rows) -> str:
        """
        Formats a list of paper data rows into a readable table.

        Each row includes the paper's title, author(s), and DOI. Missing values are replaced with '--'.
        """

        table = []

        for _, row in enumerate(rows, start=1):
            title = row["Title"] or "--"
            author = row["Author"] or "--"
            year = row["Year"] or "--"
            doi = row["DOI"] or "--"

            table.append([title, author, year, doi])

        output = ""
        col_widths = None

        if self.output_area.window.render_info:
            total_width = self.output_area.window.render_info.window_width

            # Leave a bit of space for padding/borders
            usable_width = total_width - 5  # adjust based on tablefmt

            # Assign proportions to each column
            col_widths = [
                int(usable_width * 0.5),  # Title
                int(usable_width * 0.2),  # Author(s)
                int(usable_width * 0.3),  # DOI
            ]

            output = tabulate(
                table,
                headers=["Title", "Author(s)", "Year", "DOI"],
                tablefmt="simple_grid",
                maxcolwidths=col_widths,
            )

        return output

    def command_handler(self, buffer) -> None:
        """
        Parses and handles user input commands.

        Args:
            buffer: The input buffer (unused in this method but likely required by the UI framework).
        """

        tokens = self.input_field.text.strip().split(maxsplit=2)
        if len(tokens) == 0:
            return

        # A list of arguments to pass the command functions
        main_cmd = tokens[0].lower()
        args = [tokens]

        # Get function to call based on command mapping
        func = self.commands.get(main_cmd)
        if func:
            self.output_clear()
            func(args)
        else:
            self.output_clear()
            self.output_write(f"Unknown command '{main_cmd}'")

    # Command callbacks

    def command_exit(self, args: list) -> None:
        """
        Exits the application by stopping the main loop and closing the interface.

        Args:
            args (list): List of arguments passed to the command (not used here).
        """
        print(self.application)
        self.running = False
        self.application.exit()

    def command_help(self, args: list) -> None:
        """
        Displays a list of all available commands grouped by category.

        Includes commands for listing, searching (semantic and keyword),
        database operations, and general utilities.
        """

        self.output_write(
            "Available commands:\n\n"
            "----------------- General ------------------  \n"
            " list papers                lp\n"
            "\n"
            "----- Searching by semantic similarity -----  \n"
            " simsearch  <text>          ss  <text>\n"
            " vsimsearch <text>          vss <text>\n"
            "\n"
            "------ Searching by title/author/topic -----  \n"
            " search  title  <title>     st  <title>\n"
            " search  author <name>      sa  <name>\n"
            " search  topic  <topic>     sp  <topic>\n"
            " vsearch <type> <text>     vsh <type> <text>\n"
            "\n"
            "----------------- Database -----------------  \n"
            " add <directory_path>       a <directory_path>\n"
            "\n"
            "-------------- Miscellaneous ---------------  \n"
            " help (this message)        h\n"
            " exit                       e\n"
            "\n"
        )

    def command_list_papers(self, args: list) -> None:
        """
        Lists all papers in the database.

        Accepts the command 'lp' or 'list papers'.
        Retrieves paper details and prints them in a formatted table.
        """

        # Command parsing
        tokens = args[0]
        if tokens not in (["lp"], ["list", "papers"]):
            self.output_write(f"Unknown command '{' '.join(tokens)}'")
            return

        rows = self.session.run(query_list_papers).data()
        if not rows:
            self.output_write("No papers found.")
            return

        result = self.generate_table_str(rows)

        self.output_write(f"=== {len(rows)} papers in the database ===")
        self.output_write(result)

    def command_search(self, args: list) -> None:
        """
        Dispatches a search query based on the command and value provided.

        Supports searches by title, author, or topic, with optional visualisation.
        Handles both shorthand (e.g., 'st', 'sa') and long-form commands (e.g., 'search title').

        Args:
            args (list): List of command tokens, e.g., ["search", "title", "AI"].
        """

        tokens = args[0]

        if len(tokens) < 2:
            self.output_write(f"Unknown command '{' '.join(tokens)}'")
            return

        # Handle visual search flags
        visualise = tokens[0] in {"vsearch", "vsh", "vst", "vsa", "vsp"}

        # Mapping of shorthand and long-form commands to search types
        search_map = {
            "st": "title",
            "sa": "author",
            "sp": "topic",
            "search": None,
            "vst": "title",
            "vsa": "author",
            "vsp": "topic",
        }

        cmd = tokens[0].lower()
        if cmd in {"search", "vsearch", "vsh"}:
            if len(tokens) < 3:
                self.output_write(f"Usage: {cmd} <title|author|topic> <value>")
                return
            sub_cmd = tokens[1].lower()
            value = tokens[2]
        elif cmd in search_map:
            sub_cmd = search_map[cmd]
            value = tokens[1]
        else:
            self.output_write(f"Unknown command '{cmd}'")
            return

        # Dispatch to appropriate handler
        if sub_cmd == "title":
            self.command_search_by_title(value, visualise)
        elif sub_cmd == "author":
            self.command_search_by_author(value, visualise)
        elif sub_cmd == "topic":
            self.command_search_by_topic(value, visualise)
        else:
            self.output_write("Unknown search type. Must be: title, author, or topic.")

    def command_search_by_title(self, title_value, visualsation) -> None:
        """
        Finds papers that match the given title (partial match).
        Outputs filename, title, year, DOI.
        """

        result = self.session.run(query_search_by_title, title_val=title_value).data()
        if not result:
            self.output_write(f"No papers found with title containing '{title_value}'.")
            return
        self.output_write(f"=== Papers with title containing '{title_value}' ===")
        self.output_write(self.generate_table_str(result))

        if visualsation == True:
            visualise_output(result, title_value)

    def command_search_by_author(self, author_name, visualsation) -> None:
        """
        Finds papers written by the specified author (partial match).
        Outputs author, filename, title, DOI.
        """

        result = self.session.run(query_search_by_author, author_val=author_name).data()
        if not result:
            self.output_write(
                f"No results found for author containing '{author_name}'."
            )
            return

        self.output_write(f"=== Papers by author containing '{author_name}' ===")
        self.output_write(self.generate_table_str(result))

        if visualsation == True:
            visualise_output(result, author_name)

    def command_search_by_topic(self, topic_val: str, visualsation: bool) -> None:
        """
        Searches for papers linked to a topic matching the given keyword.

        - Queries papers with related Topic nodes.
        - Displays title, filename, DOI, and topic.
        - Optionally visualises the results.

        Args:
            topic_val (str): The topic keyword to search for.
            visualsation (bool): Whether to generate a visualisation of the results.
        """

        result = self.session.run(query_search_by_topic, topic_val=topic_val).data()
        if not result:
            self.output_write(f"No papers found with topic containing '{topic_val}'.")
            return

        self.output_write(f"=== Papers with topic containing '{topic_val}' ===")
        self.output_write(self.generate_table_str(result))

        if visualsation == True:
            visualise_output(result, topic_val)

    def command_search_by_similarity(self, args: list) -> None:
        """
        Performs semantic search using SBERT-based paper embeddings.

        - Builds an embedding from the user's query.
        - Computes cosine similarity with stored paper embeddings.
        - Displays the top 15 matching papers (Title, Author, DOI, Similarity).

        Args:
            args (List[str]): Command-line input containing the search query.

        Note:
            Paper embeddings must already exist in the database.
        """

        tokens = args[0]
        if len(tokens) < 2:
            self.output_write(f"Unknown command '{' '.join(tokens)}'")
            return

        query_text = tokens[1] if len(tokens) == 2 else tokens[1] + " " + tokens[2]

        results = self.analysis.find_papers_by_similarity(
            self.session, query_text, top_n=15, threshold=0.2
        )
        if not results:
            self.output_write(
                "No papers found with embedding. Please ensure you stored them!"
            )
            return

        self.output_write(f"=== Semantic Search Results for '{query_text}' ===")
        self.output_write(
            tabulate(
                results,
                headers=["Title", "Author", "DOI", "Similarity"],
                tablefmt="simple_grid",
                maxcolwidths=50,
            )
        )

    def command_search_by_vsemantic(self, args: list) -> None:
        """
        Executes semantic search using SBERT embeddings.

        - Takes a text query from user input.
        - Computes its embedding and compares it to paper embeddings using cosine similarity.
        - Displays the top 15 matching papers with Title, Author, DOI, and Similarity.
        - Also generates a visualisation of the results.

        Args:
            args (List[str]): Command-line tokens; query formed from the second and optionally third token.

        Note:
            Paper embeddings must already be stored in the database.
        """

        tokens = args[0]
        if len(tokens) < 2:
            self.output_write(f"Unknown command '{' '.join(tokens)}'")
            return
        query_text = tokens[1] if len(tokens) == 2 else tokens[1] + " " + tokens[2]

        results = self.analysis.find_papers_by_similarity(
            self.session, query_text, top_n=15, threshold=0.2
        )
        if not results:
            self.output_write(
                "No papers found with embedding. Please ensure you stored them!"
            )

        self.output_write(f"=== Semantic Search Results for '{query_text}' ===")
        self.output_write(
            tabulate(
                results,
                headers=["Title", "Author", "DOI", "Similarity"],
                tablefmt="simple_grid",
                maxcolwidths=50,
            )
        )

        papers = [
            {"Title": title, "Author": author, "DOI": doi, "Similarity": sim}
            for title, author, doi, sim in results
        ]

        visualise_output(papers, query_text, use_similarity=True)

    def command_add_papers_by_users(self, args: list) -> None:
        """
        Loads and adds papers from a user-specified directory to the Neo4j database.

        - Extracts metadata, keywords, and embeddings from each paper.
        - Stores structured paper data (title, text, author, topics, DOI, etc.) into the graph.

        Args:
            args (List[str]): Command-line input where the second token is the directory path.
        """

        tokens = args[0]
        if len(tokens) <= 1:
            self.output_print(f"Unknown command '{' '.join(tokens)}'")
            return

        path = tokens[1]

        if not os.path.exists(path):
            self.output_print(
                f"Error: Path-'{path}' doesn't exist, please enter correct path!"
            )
            return
        if not os.path.isdir(path):
            self.output_print(
                f"Error: Path-'{path}' doesn't a folder, please enter correct path!"
            )
            return

        # Lanuch a dedicated thread so that papers will load in the background
        def paper_loading_thread():
            # (1) Load papers from local directory
            self.all_papers = papers_load(
                path, self.analysis.keyword_extractor, output_writer=self.output_print
            )
            if not self.all_papers:
                self.output_print("No valid PDF file was found.")
                return

            # (2) Write data into Neo4j
            for paper in self.all_papers:
                # Build a dictionary to pass to add_paper
                paper_data = {
                    "path": paper.path,
                    "id": paper.title,
                    "filename": paper.filename,
                    "Year": paper.year,
                    "title": paper.title,
                    "text": paper.text,
                    "authors": [paper.author] if paper.author else [],
                    "topics": paper.topics,
                    "main_keyphrase": paper.main_keyphrase,
                    "doi": paper.doi,
                }
                self.output_print(f"Uploading file: {paper.filename}.pdf")
                add_paper(self.session, self.analysis.sentence_transformer, paper_data)

            self.output_print("Paper loading complete")

        threading.Thread(target=paper_loading_thread, daemon=True).start()
