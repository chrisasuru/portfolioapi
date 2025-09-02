from ...config import settings
from fastapi import Depends

async def get_query_parameters(q: str | None = None, 
                                page: int = 1, 
                                page_size: int = settings.DEFAULT_PAGE_SIZE,
                                sort: str | None = None):

    return {"q": q, "page": page, "page_size": page_size, "sort": sort}


def get_pagination_params(query_params: dict = Depends(get_query_parameters)):
     
     return "&".join([f"{key}={value}" for key, value in query_params.items() if key != "page" and value != None])

     