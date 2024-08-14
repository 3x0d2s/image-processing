import redis
from redis.exceptions import ConnectionError, DataError, NoScriptError, RedisError, ResponseError
from functools import partial
from typing import Iterator
from image_processing import add_text_to_image
from config import config


def get_messages(r: redis.Redis, **kwargs) -> Iterator[tuple[bytes, dict]]:
    xreadgroup = partial(r.xreadgroup,
                         groupname=config.REDIS_GROUP_KEY,
                         consumername=config.REDIS_CONSUMER_NAME,
                         count=5
                         )
    [[_, messages]] = xreadgroup(**kwargs)
    while len(messages) != 0:
        for msg in messages:
            yield msg
        [[_, messages]] = xreadgroup(**kwargs)
    return


def image_processing(message_data: dict) -> bytes:
    image: bytes = message_data[b'image']
    description: str = message_data[b'description'].decode('utf-8')
    image = add_text_to_image(image, description, config.FONT_SIZE)
    return image


def processing(r: redis.Redis):
    stream_key = config.REDIS_INCOMING_STREAM_KEY
    group_key = config.REDIS_GROUP_KEY
    try:
        r.xgroup_create(name=stream_key, groupname=group_key, id=0, mkstream=True)
    except ResponseError as e:
        print(f"raised: {e}")

    # handling hung messages
    for msg in get_messages(r, streams={stream_key: '0'}):
        msg_id, data = msg

        # Checking how many times the script tried to process this message
        [msg_info] = r.xpending_range(stream_key, group_key, min=msg_id, max=msg_id, count=1)
        times_delivered = msg_info['times_delivered']
        if times_delivered >= 3:
            # This case means that an error occurs when processing this message
            pass
        else:
            new_image = image_processing(message_data=data)
            data[b'image'] = new_image
            r.xadd(config.REDIS_OUTGOING_STREAM_KEY, data)

        r.xack(stream_key, group_key, msg_id)
        r.xdel(stream_key, msg_id)

    # processing incoming messages
    for msg in get_messages(r, block=0, count=1, streams={stream_key: '>'}):
        msg_id, data = msg
        new_image = image_processing(message_data=data)
        data[b'image'] = new_image
        r.xadd(config.REDIS_OUTGOING_STREAM_KEY, data)
        #
        r.xack(stream_key, group_key, msg_id)
        r.xdel(stream_key, msg_id)

    return


def main():
    r = redis.Redis.from_url(config.REDIS_DSN)
    try:
        processing(r)
    finally:
        r.close()


if __name__ == '__main__':
    main()
