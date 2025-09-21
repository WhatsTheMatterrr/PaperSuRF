# PaperSuRF
PaperSuRF® is an academic paper search and visualisation system designed to support researchers in storing, exploring, and understanding the link between academic publications through author or keyword search, relationship mapping, and visualisations. The system is built with functionality for uploading user-owned paper collections and searching via authors or keywords. It allows users to query by topic or author, and view visual representations of the relationships between papers, authors, and keywords.

Here is our welcoming page upon the program launch:

<p float="left">
<img src=".gitlab/assets/preview_1.png" alt="Description" width="520"/>
</p>

With command `help`, users will be redirected to the help panel that shows all available query commands. Each command has their corresponding abbreviation (on the right-hand side) for quick searches, once users become familiar with the commands.

<p float="left">
<img src=".gitlab/assets/preview_2.png" alt="Description" width="520"/>
</p>

## Required Dependencies
Below is the complete list of required dependencies that must be installed prior to running PaperSuRF.
- [Python](https://www.python.org/downloads/release/python-3120/)  v3.12
- [PyMuPDF](https://pypi.org/project/PyMuPDF/1.25.2/) v1.25.2
- [sentence-transformers](https://pypi.org/project/sentence-transformers/) v3.4.1
- [keybert](https://pypi.org/project/keybert/0.8.5/) v0.8.5
- [prompt-toolkit](https://pypi.org/project/prompt-toolkit/3.0.30/) v3.0.30
- [neo4j](https://pypi.org/project/neo4j/5.28.1/) v5.28.1
- [tabulate](https://pypi.org/project/tabulate/0.9.0/) v0.9.0
- [pyvis](https://pypi.org/project/pyvis/0.3.2/) v0.3.2

Optional:
- [pytest](https://pypi.org/project/pytest/8.3.4/) v8.3.4
- [black](https://pypi.org/project/black/24.10.0/) v24.10.0


## Installation

1. First clone the repository from GitLab and enter the ```papersurf``` directory:
``` sh
git clone git@git.ecdf.ed.ac.uk:psd2425/Robinson-Fuller/papersurf.git && cd papersurf
```

_Note that if you want a local copy of papers to test the paper loading functionaility of the application, make sure you also clone the paper repository as a submodule using ```--recurse-submodules```_.

> ``` sh
> git clone --recurse-submodules git@git.ecdf.ed.ac.uk:psd2425/Robinson-Fuller/papersurf.git && cd papersurf
> ```

2. Create a Python virtual environment:
``` sh
python -m venv .venv
```

3. Activate virtual environment:
``` sh
source ./.venv/bin/activate
```

4. Install required external dependencies:
``` sh
pip install -r requirements.txt
```

## Running

Now that PaperSuRF has been fully installed along with its dependencies, you can now launch the program from the root directory:
``` sh
python papersurf
```

For further help and guided documentation, please refer to the **User Documentation** [here](https://git.ecdf.ed.ac.uk/psd2425/Robinson-Fuller/papersurf/-/tree/main/docs) or can also be found within the ```docs``` directory.

## Tests
PaperSurf includes numerious Unit Tests and test to ensure various funtionailities of the application work as expected. These can be run with the following command (Assuming the optional ```pytest``` dependency was installed):
``` sh
pytest
```


<!-- ## Summary

This repository contains a prototype for automating the processing of academic PDF papers. It consists of the following key components:

* `prototype.py`: The main Python 3 program that processes data.
* `papers.tar.gz`: A GZIP TAR file containing PDF papers and a spreadsheet mapping PDF files to their titles.
* `requirements.txt`: A list of Python libraries required for running the prototype.
* `README.md`: This documentation file.

## Run Prototype

To run this prototype program, follow these steps:

* Extract contents: Extract the contents of `papers.tar.gz` to access the `Papers/` directory and `index.xlsx`.
* Create the following Directories:

    * `Docs`
    * `Ents`
    * `JSON`
    * `data`
* Set up a virtual environment for Python:
    * Python version 3.12 or newer and Pip version 24.0 or older, are recommended for this program.
* Activate the virtual environment.
* Install Dependencies: Install the required libraries listed in `requirements.txt`.
* Run the Program by `python3 prototype.py`. -->
