# Multi-Tool AI Agent for Bangladesh

An AI agent built with LangChain that answers data questions from three Bangladesh datasets (institutions, hospitals, restaurants) using SQLite tools, and general knowledge questions using a web search tool.

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
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=openai/gpt-4o-mini
TAVILY_API_KEY=optional_tavily_key
```

Get an OpenRouter key at https://openrouter.ai/keys. Any OpenRouter model that supports tool calling works.

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
