from aiogram.fsm.state import State, StatesGroup


class BanningStatesGroup(StatesGroup):
    USER_ID = State()
    DATE_SELECTION = State()
    TIME_SELECTION = State()
    CONFIRMATION = State()


class BannedUsersSG(StatesGroup):
    USER_SELECTION = State()
    USER_INFO = State()
    