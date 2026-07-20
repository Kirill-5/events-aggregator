from typing import Optional
from app.services.events_provider_client import EventsProviderClient

class EventsPaginator:
    def __init__(self, client, changed_at: str = "2000-01-01"):
        self.client = client
        self.changed_at = changed_at
        self.cursor = None
        self.current_page = []
        self.page_index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        # если текущая страница пуста или закончилась, то загружаем следующую
        if not self.current_page or self.page_index >= len(self.current_page):
            data = await self.client.events(cursor=self.cursor, changed_at=self.changed_at)
            self.current_page = data.get("results", [])
            self.cursor = data.get("next")
            self.page_index = 0

            # Если нет ни текущей страницы ни следующей, - завершаем итерацию
            if not self.current_page and not self.cursor:
                raise StopAsyncIteration

        # если текущая страница пуста, но есть следующая, то повторяем загрузку
        if not self.current_page:
            return await self.__anext__()

        # Возвращаем один элемент и двигаем индекс
        event = self.current_page[self.page_index]
        self.page_index += 1

        # если это был последний элемент на странице, тогда обнуляем страницу
        if self.page_index >= len(self.current_page):
            self.current_page = []

        return event