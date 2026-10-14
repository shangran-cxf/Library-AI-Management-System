"""统一响应结构 {code, message, data}。"""


def ok(data=None, message: str = "success"):
    return {"code": 200, "message": message, "data": data}


def fail(code: int, message: str, data=None):
    return {"code": code, "message": message, "data": data}
