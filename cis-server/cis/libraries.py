from cis import database

conn = database.connect()


def libraries(event, context):
    result = database.query("SELECT \"method\" FROM public.pg_target group by \"method\"", conn)

    print(result)

def delete(event, context):
    pass


def exists(event, context):
    pass
