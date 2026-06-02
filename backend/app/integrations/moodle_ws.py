"""Moodle Web Services client for syncing users, activities, and grades."""

import uuid


class MoodleWSClient:
    """Async HTTP client for Moodle Web Services.

    Uses lazy import of httpx to avoid requiring it at module load time.
    """

    def __init__(self, base_url: str, token: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    async def _call(self, ws_function: str, params: dict | None = None) -> dict:
        import httpx

        url = f"{self.base_url}/webservice/rest/server.php"
        data = {
            "wstoken": self.token,
            "wsfunction": ws_function,
            "moodlewsrestformat": "json",
            **(params or {}),
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, data=data)
            resp.raise_for_status()
            return resp.json()

    async def get_users(self, user_ids: list[uuid.UUID] | None = None) -> list[dict]:
        """Retrieve user data from Moodle."""
        params: dict = {}
        if user_ids:
            params["userids"] = [str(uid) for uid in user_ids]
        return await self._call("core_user_get_users_by_id", params)  # type: ignore[return-value]

    async def get_course_users(self, course_id: int) -> list[dict]:
        """Get enrolled users in a Moodle course."""
        return await self._call("core_enrol_get_enrolled_users", {"courseid": course_id})  # type: ignore[return-value]

    async def get_grades(self, course_id: int, user_id: int | None = None) -> list[dict]:
        """Get grade items and grades for a course."""
        params = {"courseid": course_id}
        if user_id:
            params["userid"] = user_id
        return await self._call("gradereport_user_get_grade_items", params)  # type: ignore[return-value]
