from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import pyodbc

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database configuration
CONNECTION_STRING = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=ins-quebec-public.database.windows.net,1433;"
    "Database=Name;"
    "UID=vhwjebgwst;"
    "PWD=8viLo6wKD6Bht$Te;"
)

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

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)

