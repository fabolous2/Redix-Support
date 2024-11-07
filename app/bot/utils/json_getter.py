import json


def get_text_by_key(key: str) -> str:
    with open("app/bot/files/start_message.json", encoding="utf-8") as f:
        data = json.load(f)

        return data[key]
    

def edit_text_by_key(key: str, new_message: str) -> None:
    with open("app/bot/files/start_message.json", encoding="utf-8") as f:
        data = json.load(f)

    data[key] = new_message
    with open('app/bot/files/start_message.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_start_message() -> str:
    return get_text_by_key('start_message')


def edit_start_message(new_message: str) -> None:
    edit_text_by_key(key='start_message', new_message=new_message)