import grpc
from pb_grpc.companies_pb2 import Company
from pb_grpc.companies_pb2 import CreateCompanyRequest
from pb_grpc.companies_pb2 import CreateCompanyResponse
from pb_grpc.companies_pb2 import GetCompaniesRequest
from pb_grpc.companies_pb2 import GetCompaniesResponse
from pb_grpc.companies_pb2 import UpdateCompanyRequest
from pb_grpc.companies_pb2 import UpdateCompanyResponse
from pb_grpc.companies_pb2 import DeleteCompanyRequest
from pb_grpc.companies_pb2 import DeleteCompanyResponse
from pb_grpc import companies_pb2_grpc

from repository.repository_db import RepositoryDB

class CompaniesService(companies_pb2_grpc.CompaniesServiceServicer,):
	def __init__(self, repository: RepositoryDB):
		super().__init__()
		self.repository = repository

	def CreateCompany(self, request: CreateCompanyRequest, context: grpc.RpcContext) -> CreateCompanyResponse:
		company_name = request.name
		company_owner = request.owner_name
		company = Company(name=company_name, owner_name=company_owner)
		try:
			company = self.repository.save(company)
		except Exception as e:
			raise grpc.RpcError(grpc.StatusCode.INTERNAL, str(e))
		return CreateCompanyResponse(result=company)

	def GetCompanies(self, request: GetCompaniesRequest, context: grpc.RpcContext) -> GetCompaniesResponse:
		company_name = request.filter.name
		company_owner = request.filter.owner_name
		company_id = request.filter.id
		search_query = {}
		if company_id:
			company = self.repository.get(company_id)
			return GetCompaniesResponse(companies=[company])
		else:
			if company_name:
				search_query["name"] = company_name
			if company_owner:
				search_query["owner_name"] = company_owner
			companies = self.repository.get_all(search_query=search_query)
			return GetCompaniesResponse(results=companies)

	def UpdateCompany(self, request: UpdateCompanyRequest, context: grpc.RpcContext) -> UpdateCompanyResponse:
		old_company_id = request.old_company_id
		new_company = request.new_company
		# Try to see if it exists
		try:
			self.repository.get(old_company_id)
		except Exception as e:
			raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, str(e))
		try:
			company = self.repository.update(old_company_id, new_company)
		except Exception as e:
			raise grpc.RpcError(grpc.StatusCode.INTERNAL, str(e))
		return UpdateCompanyResponse(result=company)

	def DeleteCompany(self, request: DeleteCompanyRequest, context: grpc.RpcContext) -> DeleteCompanyResponse:
		company_id = request.id
		# Check if exists
		try:
			self.repository.get(company_id)
		except Exception as e:
			raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, str(e))
		try:
			self.repository.delete(company_id)
		except Exception as e:
			raise grpc.RpcError(grpc.StatusCode.INTERNAL, str(e))
		return DeleteCompanyResponse()

