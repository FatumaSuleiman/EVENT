
import firebase_admin
from firebase_admin import credentials,auth
from firebase_admin import firestore
from models import Institution
from fastapi import APIRouter  
from models import Institution,Event,TicketCategory,Ticket,User,Login
from starlette.responses import JSONResponse
from typing import List
inst_router=APIRouter()
import random
import math
from datetime import timezone,datetime
from fastapi import HTTPException,Depends
import requests
#import pyrebase
from endpoint.wrapper import encode_token,get_current_user


if not firebase_admin._apps:
    cred=credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db=firestore.client()

def rand_tick():
    num = "145689876543"
    four_digits = ""
    for i in range(4):
        four_digits = four_digits + num[math.floor(random.random() * 10)]
    return four_digits

# endPoint to create institution
    
@inst_router.post('/save/institutions',response_model=Institution,tags=['Institutions'])
async def create_institution(inst:Institution,user=Depends(get_current_user)):
    new_institution={ "name":inst.name,"phone":inst.phone,"email":inst.email,"address":inst.address,"active_status":inst.active_status}
    doc_ref=db.collection("institution")
    doc_ref.add(new_institution)
    return new_institution

# endPoint to get institution detail

@inst_router.get('/institution/detail',response_model=Institution,tags=['Institutions'])
async def get_institution(doc_id:str,user=Depends(get_current_user)):
    doc=db.collection("institution").document(doc_id).get()
    if not doc is None:
        return doc.to_dict()
    
# endPoint to get all institutions
   
@inst_router.get('/all/institutions',response_model=List[Institution],tags=['Institutions'])
async def get_all_institutions(user=Depends(get_current_user)):
    docs=db.collection("institution").get()
    doc_list=[]
    for doc in docs:
        doc_list.append(doc.to_dict())
    return doc_list

# endPoint to update institution

@inst_router.put('/update/institution',response_model=Institution,tags=['Institutions'])
async def update_institution(doc_id:str,inst:Institution,user=Depends(get_current_user)):
     institution_data={ "name":inst.name,"phone":inst.phone,"email":inst.email,"address":inst.address,"active_status":inst.active_status}     
     db.collection("institution").document(doc_id).update(institution_data)
     return  institution_data

    # endPoint to create event
@inst_router.post('/events/save',response_model=Event,tags=['Institutions'])
async def create_event(doc_id:str,ev:Event,user=Depends(get_current_user)):
    new_event={"name":ev.name,"location":ev.location,"datetime":ev.datetime,"active":ev.active}
    db.collection("institution").document(doc_id).collection("event").add(new_event)
    return new_event

    #endPoint to get event detail

@inst_router.get('/events/details',response_model=Event,tags=['Institutions'])
async def get_event(doc_id:str,document:str,user=Depends(get_current_user)):
    doc=db.collection("institution").document(doc_id).collection("event").document(document).get()
    return doc.to_dict()

# endPoint to get events of an institution

@inst_router.get('/all/events',response_model=List[Event],tags=['Institutions'])
async def get_all_events_document(doc_id:str,user=Depends(get_current_user)):
    event_list=[]
    docs=db.collection("institution").document(doc_id).collection("event").get()
    for doc in docs:
        event_list.append(doc.to_dict())
    return event_list
# endPoint to update event of an institution

@inst_router.put('/events/update',response_model=Event,tags=['Institutions'])
async def update_event(doc_id:str,document:str,ev:Event,user=Depends(get_current_user)):
    new_event={"name":ev.name,"location":ev.location,"datetime":ev.datetime,"active":ev.active}
    db.collection("institution").document(doc_id).collection("event").document(document).update(new_event)
    return new_event

# endPoint to create tickectCategory of event

@inst_router.post('/create/ticket_category',response_model=TicketCategory,tags=['Institutions'])
async def create_ticketCategory(tick:TicketCategory,doc_id:str,docum:str,user=Depends(get_current_user)):
        ev_ref=db.collection("institution").document(doc_id).collection("event")
        docs=ev_ref.document(docum).collection("ticketCategory").get()
        if len(docs)==0:
            ticketc={"name":tick.name,"price":tick.price,"is_free":tick.is_free,"is_group":tick.is_group,"category_number":tick.category_number}
            ev_ref.document(docum).collection("ticketCategory").add(ticketc)
        else:
            check=False
            if len(docs)>0:
                for d in docs:
                    dat=d.to_dict()
                    if tick.category_number==dat['category_number']:
                        check=True
                        break
            if check:
                    return JSONResponse('category_numer already exist')
            else:
                data={"name":tick.name,"price":tick.price,"is_free":tick.is_free,"is_group":tick.is_group,"category_number":tick.category_number}
                ev_ref=db.collection("institution").document(doc_id).collection("event").document(docum)
                ev_ref.collection("ticketCategory").add(data)
                return data

#endPoint to get ticket category detail

@inst_router.get('/ticketcategory/details',response_model=TicketCategory,tags=['Institutions'])
async def get_category(doc_id:str,document:str,doc3_id,user=Depends(get_current_user)):

    doc_event=db.collection("institution").document(doc_id).collection("event").document(document)
    doc_cat= doc_event.collection("ticketCategory").document(doc3_id).get()
    if not doc_cat is None:    
        return doc_cat.to_dict()
    else:
        return JSONResponse(content="ticket category does not exist")
    
    # endPoint to update ticketCategory
@inst_router.put('/ticket_category/update',response_model=TicketCategory,tags=['Institutions'])
async def update_ticket_category(doc_id1:str,doc_id2:str,doc_id3:str,tick:TicketCategory,user=Depends(get_current_user)):
    data={"name":tick.name,"price":tick.price,"is_free":tick.is_free,"is_group":tick.is_group,"category_number":tick.category_number}
    db.collection("institution").document(doc_id1).collection("event").document(doc_id2).collection("ticketCategory").document(doc_id3).update(data)
    return data
    
# endPoint to save Ticket

@inst_router.post('/tickets/event/save',response_model=Ticket,tags=['Institutions'])
async def create_tickets_event(ticket:Ticket,doc_id1:str,doc_id2:str,user=Depends(get_current_user)):
    number=rand_tick()
    data={"ticket_number":number,"ticket_categoryId":ticket.ticket_categoryId,"is_valid":ticket.is_valid,
          "validateAt":datetime.now(),"transaction_number":ticket.transaction_number}
    doc_ref=db.collection("institution").document(doc_id1).collection("event").document(doc_id2)
    doc_ref.collection("tickets").add(data)
    return JSONResponse("Ticket saved successfully")

#endpoint to get Ticket details
@inst_router.get('/ticket/details/event',tags=['Institutions'])
async def get_ticket_event_detail(doc_id1:str,doc_id2:str,doc_id3:str,user=Depends(get_current_user)):
    event_ref=db.collection("institution").document(doc_id1).collection("event").document(doc_id2)
    doc_ref=event_ref.collection("tickets").document(doc_id3).get()
    if not doc_ref is None:
        return doc_ref.to_dict()
    else:
        return JSONResponse("Ticket does not exist")
    
 # endPoint to update Ticket
@inst_router.put('/ticket/event/update',response_model=Ticket,tags=['Institutions'])
async def update_ticket(doc_id1:str,doc_id2:str,doc_id3:str,tick:Ticket,user=Depends(get_current_user)):
    new_tick_number=rand_tick()
    data={"ticket_number":new_tick_number,"ticket_categoryId":tick.ticket_categoryId,"is_valid":tick.is_valid,
          "validateAt":datetime.now(),"transaction_number":tick.transaction_number}
    db.collection("institution").document(doc_id1).collection("event").document(doc_id2).collection("tickets").document(doc_id3).update(data)
    return data
    #endPoint to get all events of each institution
    
@inst_router.get('/get/all/events',response_model=List[Event],tags=['Institutions'])
async def get_all_events_detail(doc_id1:str,user=Depends(get_current_user)):
    list_event=[]
    collections=db.collection("institution").document(doc_id1).collections()
    for collection in collections:
        for doc in collection.stream():
            list_event.append(doc.to_dict())
        return list_event
    
#endPoint to get all ticket categories  of each event

@inst_router.get('/get/ticket/categories/event',response_model=List[TicketCategory],tags=['Institutions'])
async def get_all_categories_detail(doc_id1:str,doc_id2,user=Depends(get_current_user)):
    list_categories=[]
    collections=db.collection("institution").document(doc_id1).collection("event").document(doc_id2).collections()
    for collection in collections:
        for doc in collection.stream():
            list_categories.append(doc.to_dict())
        return list_categories


#endPoint to get all tickets  of each event

@inst_router.get('/get/ticket/categories/event',response_model=List[Ticket],tags=['Institutions'])
async def get_all_tickets_detail(doc_id1:str,doc_id2:str,user=Depends(get_current_user)):
    list_tickets=[]
    collections=db.collection("institution").document(doc_id1).collection("event").document(doc_id2).collections()
    for collection in collections:
        for doc in collection.stream():
            list_tickets.append(doc.to_dict())
        return list_tickets
    
# create user endpoint
@inst_router.post('/create/users',response_model=User,tags=['Users'])
async def create_user(users:User,user=Depends(get_current_user)):
    email=users.email
    password=users.password
    
    try:
        user=auth.create_user(
            
            email=email,
            password=password,
            
        )
        return JSONResponse(content={"message":f"user created successfully for user{user.uid}"})
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400,detail=f"Account already created for the  email{email}" )
# login endpoint
@inst_router.post('/login')
async def create_access_token(login:Login):
    email=login.email
    password=login.password
    data={"email":email,
          "password":password,
          "returnSecureToken":True
        }
    response=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyBE1CFROv2B-NljsxGRFtGlCtGwuEW_qqU',data=data)
    token=response.json()
    if 'error' in token and token['error'] is not None:
        return JSONResponse(content="invalid email or password",status_code=401)
    return {'token':token}

      
