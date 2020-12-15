from django_redis import get_redis_connection

conn = get_redis_connection('default')
print(conn.get('myKey'))
