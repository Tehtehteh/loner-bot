

class ICaptchaSolver:
    async def solve_from_file(self, file_name: str) -> str:
        raise NotImplementedError

    async def solve_from_url(self, url: str) -> str:
        raise NotImplementedError
