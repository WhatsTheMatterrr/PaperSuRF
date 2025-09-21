# 📘 PaperSuRF - User Guide
This document provides user documentation and guidance on how to effectively use the **PaperSuRF** application. It includes detailed instructions for each available command, including how to search for papers by title, author, or topic, as well as how to perform a semantic similarity search. In addition to this documentation, the program also includes built-in help functionality accessible via the `help` command to quickly access information about available commands while using the application.

---
Ensure that you have fully installed the application as instructed in the [README.md](https://git.ecdf.ed.ac.uk/psd2425/Robinson-Fuller/papersurf/-/blob/main/README.md?ref_type=heads) file.


The first step is to launch PaperSuRF which can be achieved by executing the following command:
```
python papersurf
```

## 🖥️ Command Line Interface
Once launched, you’ll see the home screen, which includes a command window and an output window. Use the command window to enter your commands—results and responses will appear in the output window. Commands must follow the syntax provided.

```
PaperSuRF (c)
Academic Paper Search Tool
Robinson Fuller Ltd

Enter Command  |__________________________|

Output         |__________________________|
```


## 🧭 Available Commands
Below is the full list of commands that are available in PaperSuRF.

### 📄 General
Basic commands for retrieving a list of all available papers in the database.

- `lp` – `list papers`

### 🔍 Searching by Semantic Similarity
Search using semantic meaning of your query (not just exact matches).

- `ss <text>` – `simsearch <text>`
- `vss <text>` – `vsimsearch <text>`

- `simsearch` stands for **similarity search** — it finds papers with semantic meanings similar to your query keyword.  
- `v-` stands for **visualisation** — it displays the retrieved results as an interactive network in a `visualized_results.html` file, viewable in your browser.

### 📑 Searching by Title / Author / Topic
Search for papers based on specific metadata fields.

- `st <paper_title>` – `search title <paper_title>`
- `sa <author_name>` – `search author <author_name>`
- `sp <topic_name>` – `search topic <topic_name>`
- `vsh <title/author/topic> <text>` – `vsearch <title/author/topic> <text>`

### 📂 Database
Manage your local paper database by importing documents.

- `a <directory_path>` – `add <directory_path>`

### ⚙️ Miscellaneous
Utility commands for help menu and quitting the application.

- `h` – `help`
- `e` – `exit`
