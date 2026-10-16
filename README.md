# Multi-Tool AI Agent for Bangladesh

An AI agent built with LangChain and Claude Haiku 5.5 that answers data questions from three Bangladesh datasets (institutions, hospitals, restaurants) using SQLite tools, and general knowledge questions using a web search tool.

## Google Colab demo

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Jahid15/bangladesh-multi-tool-agent/blob/main/demo.ipynb)

The notebook already contains the outputs of a full run. To run it yourself, add `ANTHROPIC_API_KEY` (and optionally `TAVILY_API_KEY`) in the Colab **Secrets** panel, then choose **Runtime > Run all**.

## Datasets

| Dataset | Database | Table | Rows |
|---|---|---|---|
| [Institutional Information of Bangladesh](https://huggingface.co/datasets/Mahadih534/Institutional-Information-of-Bangladesh) | `databases/institutions.db` | `institutions` | 34,897 |
| [All Bangladeshi Hospitals](https://huggingface.co/datasets/Mahadih534/all-bangladeshi-hospitals) | `databases/hospitals.db` | `hospitals` | 38,886 |
| [Bangladeshi Restaurant Data](https://huggingface.co/datasets/Mahadih534/Bangladeshi-Restaurant-Data) | `databases/restaurants.db` | `restaurants` | 10,755 |

### Table schemas

**institutions**: `eiin INTEGER PRIMARY KEY, name, type, education_level, management_type, student_type, affiliation, mpo_status, division, district, thana, union_name, mauza, area_status, geographical_status, address, post_office, mobile` (TEXT unless noted)

**hospitals**: `id INTEGER PRIMARY KEY, name, name_bangla, code INTEGER, agency, type, is_private INTEGER, division, district, city_corporation, upazila, paurasava, union_name` (TEXT unless noted)

**restaurants**: `place_id TEXT PRIMARY KEY, name TEXT, address TEXT, rating REAL, number_of_reviews INTEGER, affluence INTEGER, latitude REAL, longitude REAL`

## Project structure

```
build_databases.py   Downloads the CSVs and converts them to SQLite databases
tools.py             InstitutionsDBTool, HospitalsDBTool, RestaurantsDBTool, WebSearchTool
agent.py             Main agent (LangChain AgentExecutor) with CLI
demo.ipynb           Google Colab demo notebook
databases/           Generated SQLite databases
```

## Tools

| Tool | Purpose |
|---|---|
| `InstitutionsDBTool` | Schools, colleges, madrasas, technical institutes |
| `HospitalsDBTool` | Hospitals, clinics, diagnostic centers, health offices |
| `RestaurantsDBTool` | Restaurants, ratings, reviews, locations |
| `WebSearchTool` | General knowledge (Tavily if `TAVILY_API_KEY` is set, otherwise DuckDuckGo) |

Each DB tool connects to its database in read only mode, runs the SQL query the LLM writes, and returns the rows. The agent then turns the rows into a natural language answer.

## Setup

```bash
git clone https://github.com/jahid15/bangladesh-multi-tool-agent.git
cd bangladesh-multi-tool-agent
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
```

Create a `.env` file (copy `.env.example`) and add your keys:

```
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_MODEL=claude-haiku-5-5
TAVILY_API_KEY=optional_tavily_key
```

Get an Anthropic key at https://console.anthropic.com. Get a Tavily key at https://tavily.com (optional).

The databases are already included. To rebuild them from the original CSVs:

```bash
python build_databases.py
```

## Usage

Interactive mode:

```bash
python agent.py
```

Single question:

```bash
python agent.py "How many hospitals are in Dhaka district?"
```

## Example queries

| Question | Routed to |
|---|---|
| How many hospitals are in Dhaka district? | HospitalsDBTool |
| How many private hospitals and clinics are in Chattogram division? | HospitalsDBTool |
| How many government colleges are in Rajshahi division? | InstitutionsDBTool |
| Which district has the most madrasas? | InstitutionsDBTool |
| List the top 5 rated restaurants in Dhaka with at least 100 reviews. | RestaurantsDBTool |
| What is the role of DGHS in Bangladesh? | WebSearchTool |
| What is the healthcare policy in Bangladesh? | WebSearchTool |
