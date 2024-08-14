import io
from datetime import datetime
from functools import partial
from typing import Iterator

import redis
from PIL import Image
from redis import ResponseError

from config import config
from db import SessionLocal
from models import Image as ImageModel


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


def save_image(data: dict):
    image_dt = datetime.fromtimestamp(float(data[b'dt']))
    dt_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
    image_file_name = f"image_{dt_str}.jpg"
    img = Image.open(io.BytesIO(data[b'image']))
    img.save(f"/tmp/media/{image_file_name}")
    #
    with SessionLocal() as session:
        img = ImageModel(dt=image_dt,
                         description=data[b'description'].decode('utf-8'),
                         file_path=f"/tmp/media/{image_file_name}"
                         )
        session.add(img)
        session.commit()


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
            save_image(data)
        #
        r.xack(stream_key, group_key, msg_id)
        r.xdel(stream_key, msg_id)

    # processing incoming messages
    for msg in get_messages(r, block=0, count=1, streams={stream_key: '>'}):
        msg_id, data = msg
        save_image(data)
        #
        r.xack(stream_key, group_key, msg_id)
        r.xdel(stream_key, msg_id)

    return


def main():
    r = redis.Redis.from_url(str(config.REDIS_DSN))
    try:
        processing(r)
    finally:
        r.close()


if __name__ == '__main__':
    main()
