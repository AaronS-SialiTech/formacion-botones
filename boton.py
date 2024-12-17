### AARÓN ###

import datetime
import bson.py3compat
import pydantic
import bson
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from typing import Optional, List

from bson.objectid import ObjectId
class boton(BaseModel):
    id: str
    nombre: str
    estado: bool=False
    color: str
    fechaCreacion: str=datetime.datetime.now.__str__()
    # def __init__(self,id: int, nombre: str, estado: bool, color:str, fechaCreacion: datetime):
    #     self.id=id #Id asignado al botón, no visible para el usuario
    #     self.nombre=nombre #Nombre del botón
    #     self.estado=False #Estado del botón, indicando si está pulsado
    #     self.color=color #Color del botón
    #     self.fechaCreacion=fechaCreacion #Fecha y hora de creación del botón


class BotonModel(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    nombre: str=Field(...)
    estado: bool=Field(...)
    color: str=Field(...)
    fechaCreacion: str= datetime.datetime.now().__str__()
    model_config=ConfigDict(
     populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "nombre": "Prueba",
                "estado": "False",
                "color":"Rosa",
                "fechaCreacion": datetime.datetime.now().__str__()
                
            }
        },
    )

class UpdateBotonModel(BaseModel):
    nombre: Optional[str] = None
    estado: Optional[bool] = None
    color: Optional[str]= None
    fechaCreacion: Optional[str]=datetime.datetime.now.__str__()
    model_config=ConfigDict(
     populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "nombre": "Prueba",
                "estado": "False",
                "color":"Rosa",
                "fechaCreacion": datetime.datetime.now().__str__()
                
            }
        },
    )

class botonCollection(BaseModel):
    botones: List[BotonModel]

