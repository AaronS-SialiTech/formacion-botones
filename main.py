### AARÓN ###

from boton import boton, botonCollection, BotonModel, UpdateBotonModel

import motor

from typing import Optional, List
from typing_extensions import Annotated
from pydantic import BeforeValidator
import datetime
from pymongo import ReturnDocument
from fastapi import FastAPI
from fastapi import Body, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn

from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId


app = FastAPI()

MONGO_DETAILS = "mongodb+srv://mongoFormacion:mongosiali@cluster0.um1cy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


lista_botones=[]

prueba:boton=boton(id="2",nombre='Boton2',estado=False,color='Rojo',fechaCreacion=datetime.datetime.now().__str__())
lista_botones.append(prueba)
# botones=[prueba1,prueba2]



client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
db = client.get_database("Botones")
botones_collection = db.get_collection("Botones")
if botones_collection is not None:
    print("Conexion con Mongo exitosa")
    
PyObjectId = Annotated[str, BeforeValidator(str)]


    
    
def asignar_id(): #Asigna un id a cada botón añadido. Si el id ya existe, asigna el siguiente.
    next_id=lista_botones.__len__()+1
    for x in lista_botones:
        if x.id==next_id:
            next_id+=1
    return next_id

class BotonPost(BaseModel):
    nombre:str
    color:str
    



@app.post("/post/CrearBoton") #Crea un nuevo botón, tomando como argumentos su nombre y color.
async def CrearBoton(RecibirBoton: BotonPost):
    nuevoBoton=boton(asignar_id(),RecibirBoton.nombre,False,RecibirBoton.color,datetime.datetime.now())
    lista_botones.append(nuevoBoton)
    return nuevoBoton
   
@app.get("/get/Botones")#Listado de todos los botones
async def VerBotones():
    for item in lista_botones:
        print("ID:"+item.id.__str__()+"| Nombre: "+item.nombre+"| Color: "+item.color)


@app.get("/get/LeerBoton/{nombreBoton}")  #Muestra los datos del botón indicado, tomando como argumento su nombre
async def LeerBoton(nombreBoton:str):
     for item in lista_botones:
        if item.nombre==nombreBoton:
            return item
     

@app.put("/put/EditarBoton/{nombreBoton}") #Edita los datos del botón indicado, tomando como argumento su nombre
async def EditarBoton(nombreBoton:str, color:str):
    
    for item in lista_botones:
        if item.nombre==nombreBoton:
            item.color=color
            lista_botones.remove(item.id)
            lista_botones.append(item)
            return item
    return None
        
@app.delete("/delete/BorrarBoton/{nombreBoton}") #Elimina el botón indicado, tomando como argumento su nombre
async def BorrarBoton(nombreBoton:str):
    for item in lista_botones:
        if item.nombre==nombreBoton:
            lista_botones.remove(item)
            return True
    return False

@app.get(
    "/get/listaBotones/",
    response_description="Lista todos los botones registrados",
    response_model=botonCollection,
    response_model_by_alias=False,
)
async def listar_botones(): #MONGODB: Devuelve un listado de todos los botones
    
    botones_raw = await botones_collection.find().to_list(1000)

    botones = []
    for boton in botones_raw:
        boton["_id"] = str(boton["_id"])  
        botones.append(boton)

    return botonCollection(botones=botones)
   
@app.get(
    "/get/ObtenerBoton/{nombre}",
    response_description="Devuelve el botón especificado de la base de datos",
    response_model=botonCollection,
    response_model_by_alias=False,
)
async def obtener_boton(nombre:str):
    ver_boton=await botones_collection.find_one({"nombre": str(nombre)})
    if ver_boton is not None:
        return ver_boton
    raise HTTPException(status_code=404, detail=f"Boton {nombre} no encontrado")

@app.post(
    "/post/AnadirBoton/",
          response_description="Añade un nuevo botón",
          response_model=BotonModel,
          status_code=status.HTTP_201_CREATED,
          response_model_by_alias=False,
          )
async def NuevoBoton(item: BotonModel = Body(...)): #MONGODB: Añade un botón a la base de datos
    
    nuevoBoton=await botones_collection.insert_one(item.model_dump(by_alias=True, exclude=['id']))
    creado=await botones_collection.find_one({"_id":nuevoBoton.inserted_id})
    if creado is not None:
        creado["_id"] = str(creado["_id"])  
        del creado["_id"] 
        return creado
       
@app.put(
    "/put/ActualizarBoton/{nombre}",
    response_description="Actualizar un boton preexistente",
    response_model=BotonModel,
    response_model_by_alias=False,
)
async def ActualizarBoton(nombre:str, ActBoton: UpdateBotonModel=Body(...)): #MONGODB: Actualiza un botón en la base de datos
    ActBoton = {k: v for k, v in ActBoton.model_dump(by_alias=True).items() if v is not None}
    
    if len(ActBoton) >= 1:
            update_result = await botones_collection.find_one_and_update(
                {"nombre": str(nombre)},
                {"$set": ActBoton},
                return_document=ReturnDocument.AFTER,
            )
            if update_result is not None:
                
                update_result["_id"] = str(update_result["_id"]) 
                return update_result
               
            else:
                raise HTTPException(status_code=404, detail=f"Boton {nombre} no encontrado")
    
        
    boton_existe = await botones_collection.find_one({"nombre": nombre})
    if boton_existe is not None:
        boton_existe["_id"] = str(boton_existe["_id"])
        return boton_existe

    raise HTTPException(status_code=404, detail=f"Boton {nombre} no encontrado")

@app.delete("/delete/LimpiarBotones",
            response_description="Limpia la tabla en la base de datos",
            status_code=204,
            )
async def LimpiarTabla(): #MONGODB: Borra todas las entradas de la colección en la base de datos
    result = await botones_collection.delete_many({})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tabla vacía")
    
    return {"detail": "Todos los botones han sido borrados"}

@app.delete(
    "/delete/EliminarBoton/{nombre}",
    response_description="Eliminar un boton de la base de datos",
)
async def EliminarBoton(nombre:str): #MONGODB: Elimina el botón indicado de la base de datos
    delete_result = await botones_collection.delete_one({"nombre": str(nombre)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Botón {nombre} no encontrado")