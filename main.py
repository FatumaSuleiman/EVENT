from fastapi import FastAPI

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from models import Institution
from endpoint.institution_endPoints import inst_router


app=FastAPI() 
app.include_router(inst_router)





#@app.get('/hello')
#async def get():
    #return 'this is the Event App'


#if __name__=='__main__':
  #  uvicorn.run('main:app')
