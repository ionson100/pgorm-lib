import json



def get_json(ob:any) ->str|None:
    if ob is None:
        return None
    if hasattr(ob, 'toJson'):
         return ob.toJson()
    else:
        j = str(json.dumps(ob))
        return j




def get_object_from_json(o:any):
    if o is None:
        return None
    return o


