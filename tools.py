import os
import sqlite3

from langchain_core.tools import Tool

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases")
MAX_ROWS = 50


def get_schema(db_name):
    with sqlite3.connect(os.path.join(DB_DIR, f"{db_name}.db")) as conn:
        columns = conn.execute(f"PRAGMA table_info({db_name})").fetchall()
    return ", ".join(f"{c[1]} {c[2]}" for c in columns)


def run_query(db_name, query):
    query = query.strip().strip("`").removeprefix("sql").strip().rstrip(";")
    if not query.lower().startswith(("select", "with")):
        return "Only SELECT queries are allowed."
    path = os.path.join(DB_DIR, f"{db_name}.db")
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as conn:
            cursor = conn.execute(query)
            headers = [d[0] for d in cursor.description]
            rows = cursor.fetchmany(MAX_ROWS + 1)
    except sqlite3.Error as e:
        return f"SQL error: {e}. Check the column names and try again."
    if not rows:
        return "The query returned no results."
    lines = [" | ".join(headers)] + [" | ".join(str(v) for v in row) for row in rows[:MAX_ROWS]]
    if len(rows) > MAX_ROWS:
        lines.append(f"(showing first {MAX_ROWS} rows only)")
    return "\n".join(lines)


def make_db_tool(name, db_name, description, notes):
    schema = get_schema(db_name)
    return Tool(
        name=name,
        func=lambda query: run_query(db_name, query),
        description=(
            f"{description} Input must be a single SQLite SELECT query on table "
            f"'{db_name}' with columns: {schema}. {notes} "
            "Use LIKE with % for partial text matches. Returns query rows as text."
        ),
    )


institutions_tool = make_db_tool(
    "InstitutionsDBTool",
    "institutions",
    "Answers questions about educational institutions in Bangladesh: schools, colleges, madrasas, universities and technical institutes.",
    "type values: School, Madrasha, College, Technical and Vocational, School and College. "
    "management_type values include GOVERNMENT and NON-GOVERNMENT. "
    "division, district and thana are Title Case, for example 'Dhaka'. mpo_status is YES or NO.",
)

hospitals_tool = make_db_tool(
    "HospitalsDBTool",
    "hospitals",
    "Answers questions about hospitals, clinics, diagnostic centers and health facilities in Bangladesh.",
    "type values include Community Clinic, Consultancy & Diagnostic Center, Private Hospital / Clinic, "
    "Upazila Health Complex, District/General Hospital, Medical College Hospital, Blood Bank, 20-bed Hospital.is_private is 1 for private, 0 for public. "
    "agency values include DGHS, DGFP. division and district are Title Case, for example 'Dhaka'.",
)

restaurants_tool = make_db_tool(
    "RestaurantsDBTool",
    "restaurants",
    "Answers questions about restaurants and food places in Bangladesh, including ratings, reviews and locations.",
    "rating is 0 to 5 (0 means not rated). There is no city column, so filter location with address LIKE '%Dhaka%'. "
    "Cuisine can be guessed from name, for example name LIKE '%Biryani%'.",
)


def make_web_search_tool():
    if os.getenv("TAVILY_API_KEY"):
        from langchain_tavily import TavilySearch

        search = TavilySearch(max_results=5)

        def run(query):
            results = search.invoke({"query": query}).get("results", [])
            return "\n\n".join(f"{r['title']}\n{r['url']}\n{r['content']}" for r in results)
    else:
        from ddgs import DDGS

        def run(query):
            results = DDGS().text(query, max_results=5)
            return "\n\n".join(f"{r['title']}\n{r['href']}\n{r['body']}" for r in results)

    return Tool(
        name="WebSearchTool",
        func=run,
        description=(
            "Searches the web for general knowledge, definitions, policies, news and cultural context about Bangladesh. "
            "Use it when the question is not about counting or listing records in the institutions, hospitals or restaurants databases. "
            "Input is a search query."
        ),
    )


def get_tools():
    return [institutions_tool, hospitals_tool, restaurants_tool, make_web_search_tool()]
