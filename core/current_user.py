class CurrentUser:
    _instance = None
    _user_id: int = 1

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def id(self) -> int:
        return self._user_id


current_user = CurrentUser()


def get_current_user_id() -> int:
    """Возвращает ID текущего пользователя (singleton)"""
    return current_user.id
