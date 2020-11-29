from enum import Enum


class Status(Enum):
    success = 0
    no_auth = 3001
    token_exp = 3002
    other = 4000


class Message(Enum):
    success = "success"
    no_auth = "auth fail"
    other = "error happened"


def show_reponse(code=Status.success, data=None, message=None):
    if not message:
        if code.name in Message.__members__:
            message = Message[code.name].value
        else:
            message = Message.other.value
    ret = {"code": code.value, "message": message}
    if data:
        ret["data"] = data
    return ret