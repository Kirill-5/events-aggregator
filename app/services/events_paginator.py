class EventsPaginator:
    def __init__(self, client, changed_at: str = "2000-01-01"):
        self.client = client
        self.changed_at = changed_at
        self.cursor = None
        self.current_page = []
        self.page_index = 0
        self.page_count = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.current_page or self.page_index >= len(self.current_page):

            if self.page_count >= 40:
                raise StopAsyncIteration

            data = await self.client.events(cursor=self.cursor, changed_at=self.changed_at)
            self.current_page = data.get("results", [])
            self.cursor = data.get("next")
            self.page_index = 0
            self.page_count += 1

            if not self.current_page and not self.cursor:
                raise StopAsyncIteration

        if not self.current_page:
            return await self.__anext__()

        event = self.current_page[self.page_index]
        self.page_index += 1

        if self.page_index >= len(self.current_page):
            self.current_page = []

        return event