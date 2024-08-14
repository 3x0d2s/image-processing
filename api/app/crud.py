from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from models import Request as RequestModel
from models import RequestLog as RequestLogModel


class Request:

    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    def create(self, login: str, password: str) -> RequestModel:
        request = RequestModel(login=login, password=password)
        self.db.add(request)
        return request

    async def get_request(self, request_id: int) -> RequestModel:
        query = select(RequestModel).filter(RequestModel.id == request_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def commit(self) -> None:
        await self.db.commit()
        return

    async def refresh(self, instance: object) -> None:
        await self.db.refresh(instance)
        return


class RequestLog:

    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    def create(self, request_id: int, data: str) -> RequestLogModel:
        request_log = RequestLogModel(request_id=request_id, data=data)
        self.db.add(request_log)
        return request_log

    async def commit(self) -> None:
        await self.db.commit()
        return

    async def refresh(self, instance: object) -> None:
        await self.db.refresh(instance)
        return
