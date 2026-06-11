
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

import uvicorn
import os, random
from database import Database

db = Database('assets/recipes/list.json')
app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/styles", StaticFiles(directory="css"), name="styles")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,  "recipes": db.getAll('recipes'),
            "categories":  db.getAll('categories')
        }
    )

@app.get("/recipe", response_class=HTMLResponse)
async def recipe(request: Request, id: int | None = None):
    recipe = db.get(str(id), 'recipes')
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return templates.TemplateResponse(
        request,
        "recipe.html",
        {
            "request": request,  "recipe": { "id": id, **recipe },
            "recipes": db.getAll('recipes', 'category', recipe['category']),
            "category": db.get(recipe['category'], 'categories'),
        }
    )
    
@app.get("/recipes", response_class=HTMLResponse)
async def recipes(request: Request, category: str | None = None):
    if category:
        cat = db.get(category, 'categories')
        if not cat and category:
            raise HTTPException(status_code=404, detail="Category not found")
    else: cat = None
    
    return templates.TemplateResponse(
        request,
        "recipes.html",
        {
            "request": request,  "category": cat,
            "recipes":  db.getAll('recipes', 'category', category) if cat else db.getAll('recipes'),
            "categories": { cat['id']: cat['name'] for cat in db.getAll('categories') }
        }
    )
    
@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        request, "error.html",
        {
            "request": request,
            "code": exc.status_code,
            "text": exc.detail
        },
        status_code=exc.status_code
    )
    
@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request, "error.html",
        {
            "request": request,
            "code": 500,
            "text": "Something went wrong"
        },
        status_code=500
    )
    
@app.get("/random", response_class=RedirectResponse)
async def random_recipe(request: Request):
    recipe = random.choice(db.getAll('recipes'))
    return RedirectResponse(f'/recipe?id={recipe.get("id", 0)}')

@app.get("/favicon.ico")
def favicon():
    return FileResponse(os.path.join("assets", "favicon.png"))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7001)