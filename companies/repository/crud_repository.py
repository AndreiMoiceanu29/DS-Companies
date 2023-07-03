from .repository_interface import IRepository
from database import MongoDatabase
from bson import ObjectId
from database import MongoDatabase
from collections.abc import Generator
from logger import mge_log
from google.protobuf.json_format import MessageToDict, ParseDict
from exceptions import NotFound, InvalidId, FieldNotSet
import copy


class CRUDRepository(IRepository):
    """ CRUD Repository Database """

    database: MongoDatabase

    def __init__(self, database: MongoDatabase) -> None:
        self.database = database
        self.object_type = None
        self.collection = None

    def _set_object_type(self, object_type: object) -> None:
        self.object_type = object_type

    def _set_collection(self, collection: str) -> None:
        self.collection = collection

    def get(self, id: str) -> object:
        """ Get object from database """

        if not self.object_type:
            raise FieldNotSet("object_type not set")
        if not self.collection:
            raise FieldNotSet("collection not set")

        if not ObjectId.is_valid(id):
            raise InvalidId("Invalid id")

        collection = self.database.get_collection(self.collection)
        db_object = collection.find_one({"_id": ObjectId(id)})
        
        if db_object:
            db_object["id"] = str(db_object.pop("_id"))
            return ParseDict(db_object, self.object_type())
        
        raise NotFound(f'id "{id}" not found')
    

    def get_all(self, search_query: dict = None, sort_query: dict = None, limit: int = 0):
        """ Get all objects from database """
        if not self.object_type:
            raise FieldNotSet("object_type not set")
        if not self.collection:
            raise FieldNotSet("collection not set")

        collection = self.database.get_collection(self.collection)
        if search_query:
            db_objects = collection.find(search_query)
        else:
            db_objects = collection.find({})
        
        if sort_query:
            db_objects = db_objects.sort(sort_query)
        
        if limit:
            db_objects = db_objects.limit(limit)

        if not db_objects:
            raise NotFound("No objects found")

        for db_object in db_objects:
            if not db_object:
                continue
            db_object_copy = copy.deepcopy(db_object)
            db_object_copy["id"] = str(db_object_copy.pop("_id"))

            db_object_copy = ParseDict(db_object_copy, self.object_type())

            yield db_object_copy


    def save(self, save_object: object) -> object:
        """ Save object to database """

        if not self.object_type:
            raise FieldNotSet("object_type not set")
        if not self.collection:
            raise FieldNotSet("collection not set")

        collection = self.database.get_collection(self.collection)
        mge_log.info(f"save_object: {save_object}")
        object_dictionary = MessageToDict(save_object, 
            including_default_value_fields=True,
            preserving_proto_field_name=True
        )

        if "id" in object_dictionary:
            del object_dictionary["id"]

        response = collection.insert_one(object_dictionary)

        return self.get(response.inserted_id)


    def update(self, id: str, update_object: object) -> object:
        """ Update object to database """

        if not self.object_type:
            raise FieldNotSet("object_type not set")
        if not self.collection:
            raise FieldNotSet("collection not set")

        collection = self.database.get_collection(self.collection)
        object_dictionary = MessageToDict(update_object,
            including_default_value_fields=True,
            preserving_proto_field_name=True
        )

        if "id" in object_dictionary:
            del object_dictionary["id"]

        response = collection.update_one({"_id": ObjectId(id)}, {"$set": object_dictionary})

        # if response.modified_count == 0:
        if response.matched_count == 0:
            raise NotFound(f'id "{id}" not found ')

        return self.get(id)


    def delete(self, id: str) -> None:
        """ Delete location from database """

        if not self.object_type:
            raise FieldNotSet("object_type not set")
        if not self.collection:
            raise FieldNotSet("collection not set")

        collection = self.database.get_collection(self.collection)

        if not ObjectId.is_valid(id):
            raise InvalidId("Invalid id")

        db_object = self.get(id)

        response = collection.delete_one(
            {
                "_id": ObjectId(id)
            }
        )

        if response.deleted_count == 0:
            raise NotFound(f'id "{id}" not found')
        
        return db_object