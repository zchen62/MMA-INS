from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import pyodbc
import pandas as pd
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database configuration
CONNECTION_STRING = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:ins-quebec-public.database.windows.net,1433;"
    "Database=ins-quebec-public;"
    "Uid=vhwjebgwst;"
    "Pwd=8viLo6wKD6Bht$Te;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

# Local CSV file path
CSV_FILE_PATH = "files/athleteID_listeGDS_mcgillMMA(in).csv"  # Update this with your actual CSV file name

def insert_name(name: str) -> str:
    try:
        connection = pyodbc.connect(CONNECTION_STRING)
        cursor = connection.cursor()
        # Insert the name
        sql = "INSERT INTO Name (clientname) VALUES (?)"
        cursor.execute(sql, (name,))
        connection.commit()
        return "Successfully added to database!"
    except pyodbc.Error as e:
        error_message = f"Database error: {str(e)}"
        print(error_message)
        return error_message
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('index.html', {"request": request})

@app.get('/favicon.ico')
async def favicon():
    file_name = 'favicon.ico'
    file_path = './static/' + file_name
    return FileResponse(path=file_path, headers={'mimetype': 'image/vnd.microsoft.icon'})

@app.post('/hello', response_class=HTMLResponse)
async def hello(request: Request, name: str = Form(...)):
    if name:
        print('Request for hello page received with name=%s' % name)
        # Insert name into database and get status message
        db_message = insert_name(name)
        return templates.TemplateResponse('hello.html', {
            "request": request, 
            'name': name,
            'db_message': db_message
        })
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)

@app.get("/data-imported", response_class=HTMLResponse)
async def show_data(request: Request):
    try:
        # Check if file exists
        if not os.path.exists(CSV_FILE_PATH):
            raise FileNotFoundError(f"CSV file not found at {CSV_FILE_PATH}")
        
        # Read CSV into pandas DataFrame
        df = pd.read_csv(CSV_FILE_PATH, encoding='iso-8859-1')
        
        # Get first 5 rows and convert to HTML table
        table_html = df.head().to_html(classes=['table', 'table-striped'])
        
        return templates.TemplateResponse(
            'data_imported.html',
            {
                "request": request,
                "table": table_html
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            'data_imported.html',
            {
                "request": request,
                "error": f"Error loading data: {str(e)}"
            }
        )

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)

