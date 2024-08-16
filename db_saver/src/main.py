import io
import logging
import reprlib
from datetime import datetime
from functools import partial
from typing import Iterator
import psycopg2

import redis
from PIL import Image
from redis import ResponseError

from .config import config

logging.basicConfig(level=logging.INFO, filename="src/logs/log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")
a_repr = reprlib.Repr()


def get_messages(r: redis.Redis, **kwargs) -> Iterator[tuple[bytes, dict]]:
    """ Генератор, отдающий входящие сообщения """
    xreadgroup = partial(r.xreadgroup,
                         groupname=config.REDIS_DB_SAVER_GROUP_KEY,
                         consumername=config.REDIS_DB_SAVER_CONSUMER_NAME,
                         count=5
                         )
    [[_, messages]] = xreadgroup(**kwargs)
    while len(messages) != 0:
        for msg in messages:
            logging.info("New message: " + a_repr.repr(msg))
            yield msg
        [[_, messages]] = xreadgroup(**kwargs)
    return


def save_data_to_db(dt, description, file_path):
    try:
        conn = psycopg2.connect(str(config.PG_DSN))
        cur = conn.cursor()
        cur.execute('INSERT INTO "Image" (dt, description, file_path) VALUES (%s, %s, %s)',
                    (dt, description, file_path))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"Data saving error: {e}")
        raise e


def save_image(data: dict):
    image_dt = datetime.fromtimestamp(float(data[b'dt']))
    dt_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
    image_file_name = f"image_{dt_str}.jpg"
    img = Image.open(io.BytesIO(data[b'image']))
    img.save(f"src/media/{image_file_name}")
    logging.info("The image was saved successfully")
    #
    save_data_to_db(image_dt,
                    data[b'description'].decode('utf-8'),
                    f"src/media/{image_file_name}")
    logging.info("An entry with this image has been added to the database")


def processing(r: redis.Redis):
    stream_key = config.REDIS_STREAM_TO_DB_SAVER_NAME
    group_key = config.REDIS_DB_SAVER_GROUP_KEY
    try:
        r.xgroup_create(name=stream_key, groupname=group_key, id=0, mkstream=True)
    except ResponseError as e:
        logging.error(f"raised: {e}")

    logging.info("Handling hung messages")
    for msg in get_messages(r, streams={stream_key: '0'}):
        msg_id, data = msg
        # Checking how many times the script tried to process this message
        [msg_info] = r.xpending_range(stream_key, group_key, min=msg_id, max=msg_id, count=1)
        times_delivered = msg_info['times_delivered']
        if times_delivered >= 3:
            # This case means that an error occurs when processing this message
            logging.error(f'The script cannot process this message: {a_repr.repr(data)}')
        else:
            save_image(data)
        #
        r.xack(stream_key, group_key, msg_id)
        r.xdel(stream_key, msg_id)

    logging.info("Waiting for new messages...")
    for msg in get_messages(r, block=0, count=1, streams={stream_key: '>'}):
        msg_id, data = msg
        save_image(data)
        #
        r.xack(stream_key, group_key, msg_id)
        r.xdel(stream_key, msg_id)

    return


def main():
    logging.warning("Starting up")
    r = redis.Redis.from_url(str(config.REDIS_DSN))
    try:
        processing(r)
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        raise e
    finally:
        r.close()


if __name__ == '__main__':
    main()
