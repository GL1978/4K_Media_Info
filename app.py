import math
from globals import media_info_table_columns
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="templates")
db_path = "D:/MakeMKV/media_info/media_info.db"
items_per_page = 10  # Define the number of items per page


# Function to search media_info.db
def search_media_info(query, page):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Calculate the offset based on the current page and items per page
    offset = (page - 1) * items_per_page

    # Construct the WHERE clause dynamically to search all columns
    where_clause = " OR ".join([f"{col} LIKE ?" for col in media_info_table_columns])

    # Execute SQL query to search with pagination
    cursor.execute(
        f"SELECT * FROM (SELECT *, ROW_NUMBER() OVER () AS row_num FROM media_info WHERE {where_clause}) AS temp "
        f"WHERE row_num BETWEEN ? AND ?",
        (['%' + query + '%'] * len(media_info_table_columns) + [offset + 1, offset + items_per_page]))
    rows = cursor.fetchall()
    # Count total rows to calculate total pages
    cursor.execute(f"SELECT COUNT(*) FROM media_info WHERE {where_clause}", (['%' + query + '%'] * len(media_info_table_columns)))
    total_rows = cursor.fetchone()[0]
    # Calculate total pages
    total_pages = math.ceil(total_rows / items_per_page)
    conn.close()
    return rows, total_pages


@app.get("/", response_class=HTMLResponse)
async def search_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/static/css/style.css")
async def styles():
    return FileResponse("static/css/style.css")


@app.get("/search/", response_class=HTMLResponse)
async def search_results(request: Request, query: str, page: int = 1):
    search_results, total_pages = search_media_info(query, page)
    return templates.TemplateResponse("search_results.html",
                                      {"request": request,
                                       "query": query,
                                       "search_results": search_results,
                                       "total_pages": total_pages,
                                       "current_page": page})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
