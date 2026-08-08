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
        if not self.current_page or self.page_index >= len(self.current_page):
            data = await self.client.events(cursor=self.cursor, changed_at=self.changed_at)
            self.current_page = data.get("results", [])
            next_cursor = data.get("next")
            if next_cursor:
                if "cursor=" in next_cursor:
                    self.cursor = next_cursor.split("cursor=")[-1]
                else:
                    self.cursor = next_cursor.split("?")[0]
            else:
                self.cursor = None
            self.page_index = 0

            if not self.current_page and not self.cursor:
                raise StopAsyncIteration

        if not self.current_page:
            return await self.__anext__()

        event = self.current_page[self.page_index]
        self.page_index += 1

        if self.page_index >= len(self.current_page):
            self.current_page = []

        return event