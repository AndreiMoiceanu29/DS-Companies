from .crud_repository import CRUDRepository
from database import MongoDatabase
from pb_grpc.companies_pb2 import Company


class RepositoryDB(CRUDRepository):
    def __init__(self, database: MongoDatabase) -> None:
        super().__init__(database)
        self._set_object_type(Company)
        self._set_collection("companies")