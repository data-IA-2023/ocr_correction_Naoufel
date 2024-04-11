from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from modele import *
####
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, Date, select, update, delete
from sqlalchemy.orm import relationship, sessionmaker, Session, mapped_column, declarative_base
from sqlalchemy import create_engine
import os, dotenv, requests, datetime, json, math, subprocess, re, glob
from datetime import datetime
####
app = FastAPI()

app.mount("/statics", StaticFiles(directory="statics"), name="statics")


templates = Jinja2Templates(directory="templates")
print("start controler")



@app.get("/newfac", response_class=HTMLResponse)
def read_item(request: Request, num=None):
            Facture.read_file(num)
            with Session(engine) as session:
                query = select(Facture)
                res = session.execute(query).all()
                return templates.TemplateResponse(
                    request=request, name="index.html", context={"res":res})


