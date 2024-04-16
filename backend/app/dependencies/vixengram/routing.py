import inspect
from collections import defaultdict
from functools import wraps
from typing import Callable, Coroutine, Dict, List, Optional

from pydantic import BaseModel

from dependencies.vixengram.api import BotAPI
from dependencies.vixengram.filters.base import FilterObject


class Router:
    def __init__(
            self,
            title: str | None = None,
            tags: List[str] | None = None
    ):
        """
        Title need for OpenAPI generator
        Tags need for OpenAPI generator
        """
        self.__title = title
        self.__tags = tags
        self.__paths: Dict[Callable, List[FilterObject]] = defaultdict(list)
        self.__included_routers: List['Router'] = []
        self.__paths_with_included: Dict[Callable, List[FilterObject]] = self.__paths.copy()
        # todo: add Middleware class
        self.__middlewares: List = []

    # async def __call_middlewares(self, handler: Optional[Callable] = None, input_object: Optional[BaseModel] = None):
    #     for middleware in self.__middlewares:
    #         await middleware()
    #
    #     for router in self.__included_routers:
    #         if handler in router:
    #             await router.__call_middlewares(input_object=input_object)

    async def call_handler(self, input_object: BaseModel):
        for handler, filters in self.__paths_with_included.items():
            for filter_ in filters:
                if filter_ is None or filter_.condition_request(input_object):
                    # await self.__call_middlewares(handler=handler, input_object=input_object)

                    parameters = {}
                    need_parameters = inspect.signature(handler).parameters
                    for need_param in need_parameters:
                        # todo: add dynamic arguments
                        if "bot" in need_param:
                            parameters["bot"] = BotAPI(input_object)
                    await handler(**parameters)

    def add_route(self, filter_: FilterObject, handler: Callable[..., Coroutine]) -> None:
        self.__paths[handler].append(filter_)
        self.__paths_with_included[handler].append(filter_)

    def message(self, filter_: FilterObject | None = None):
        def decorator(fn):
            @wraps(fn)
            async def wrapper(*args, **kwargs) -> Coroutine:
                return await fn(*args, **kwargs)

            self.add_route(filter_, wrapper)
            return wrapper

        return decorator

    def include_router(self, router: 'Router'):
        self.__included_routers.append(router)
        self.__paths_with_included.update(router.__paths)
