from aiogram.fsm.state import State, StatesGroup


class StartMessageStatesGroup(StatesGroup):
    NEW_MESSAGE = State()