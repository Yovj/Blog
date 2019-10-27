from rest_framework.response import Response



class HttpCode(object):
    ok = 0
    fail = 1

def result(code=HttpCode.ok,message="",data=None,kwargs=None):
    json_dict = {"code":code,"msg":message,"data":data}

    if kwargs and isinstance(kwargs,dict) and kwargs.keys():
        json_dict.update(kwargs)
    return Response(json_dict)

def ok(data=None,message="",kwargs=None):
    return result(code=HttpCode.ok,message=message,data=data,kwargs=kwargs)

def fail(data=None,message="",kwargs=None):
    return result(code=HttpCode.fail,message=message,data=data,kwargs=kwargs)



