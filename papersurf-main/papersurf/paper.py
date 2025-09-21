# Copyright (c) 2025 Robinson Fuller Ltd
# Licensed under the MIT License.

import os
import pymupdf
import re


class Paper:
    def __init__(self):
        """
        Initializes a Document instance with default attributes.

        Attributes:
            path (str): The file path of the document.
            filename (str): The name of the document file.
            title (str): The title of the document.
            author (str): The author of the document.
            subject (str): The subject of the document.
            text (str): The extracted text content of the document.
            topics (list): A list of topics related to the document.

        All attributes are initialized with empty values.
        """

        self.path = str()
        self.filename = str()
        self.year = str()
        self.title = str()
        self.author = str()
        self.subject = str()
        self.text = str()

        self.topics = []
        self.main_keyphrase = "No keyphrase"
        self.doi = []

    def load(self, path: str) -> bool:
        """
        Loads a PDF file and extracts its metadata and text content.

        Args:
            path (str): The file path of the PDF to be loaded.

        Returns:
            bool: True if the PDF is successfully loaded, False otherwise.

        The function extracts the following metadata:
            - `self.path`: The file path of the loaded PDF.
            - `self.filename`: The filename of the PDF.
            - `self.title`: The document's title (if available).
            - `self.author`: The document's author (if available).
            - `self.subject`: The document's subject (if available).
            - `self.text`: The extracted text content from all pages of the PDF.

        Uses `pymupdf.open()` to open and process the document.
        """

        loaded = False
        with pymupdf.open(path) as document:
            self.path = path
            self.filename = os.path.basename(path)
            self.title = document.metadata.get("title", "")

            creation_date = document.metadata.get("creationDate", "")
            match = re.search(r"D:(\d{4})", creation_date)
            self.year = match.group(1) if match else ""

            self.author = document.metadata.get("author", "")
            self.subject = document.metadata.get("subject", "")
            self.text = "".join(page.get_text() for page in document)
            loaded = True

        return loaded
