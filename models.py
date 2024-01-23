from pydantic import BaseModel
from datetime import date,time,datetime
class Institution(BaseModel):
    name:str
    phone:str
    email:str
    address:str
    active_status:bool

class Event(BaseModel):
    name:str
    location:str
    datetime:datetime
    active:bool

class TicketCategory(BaseModel):
    name:str
    price:int
    is_free:bool
    is_group:bool
    category_number:str

class Ticket(BaseModel):
    ticket_categoryId:str
    ticket_number:int
    is_valid:bool
    transaction_number:int
    validatedAt:datetime
class User(BaseModel):
    email:str
    password:str
class Login(BaseModel):
    email:str
    password:str

