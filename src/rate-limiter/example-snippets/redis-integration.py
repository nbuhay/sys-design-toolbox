import redis

r = redis.Redis(
    host='localhost',
    port=6379
)

r.set('foo', 'bar')
r.set('hello', 'there')

print(r.get('foo'))
print(r.get('hello'))