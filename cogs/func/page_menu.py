from nextcord.ext import menus

class MyPageSource(menus.ListPageSource):
    def __init__(self, data, per_page, header=None):
        # this is where you can set how many items you want per page
        super().__init__(data, per_page=per_page)
        self.header = header

    async def format_page(self, menu, entries):
        # this is where you can format the entries for the page
        if self.per_page == 1:
            return entries
        if self.header:
            return self.header + "\n" + "\n".join(entries)
        else: 
            return "\n".join(entries)