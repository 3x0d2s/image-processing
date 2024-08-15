import reprlib
from functools import partial
from typing import Iterator
import logging

import redis
from redis.exceptions import ResponseError

from .config import config
from .image_processing import add_text_to_image

logging.basicConfig(level=logging.INFO, filename="src/logs/log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")
a_repr = reprlib.Repr()


def get_messages(r: redis.Redis, **kwargs) -> Iterator[tuple[bytes, dict]]:
    """ Генератор, отдающий входящие сообщения """
    xreadgroup = partial(r.xreadgroup,
                         groupname=config.REDIS_IMAGE_HANDLER_GROUP_KEY,
                         consumername=config.REDIS_IMAGE_HANDLER_CONSUMER_NAME,
                         count=5
                         )
    [[_, messages]] = xreadgroup(**kwargs)
    while len(messages) != 0:
        for msg in messages:
            logging.info("New message: " + a_repr.repr(msg))
            yield msg
        [[_, messages]] = xreadgroup(**kwargs)
    return


def image_processing(message_data: dict) -> bytes:
    image: bytes = message_data[b'image']
    description: str = message_data[b'description'].decode('utf-8')
    image = add_text_to_image(image, description, config.FONT_NAME, config.FONT_SIZE)
    logging.info("The image has been processed successfully")
    return image


def processing(r: redis.Redis):
    stream_key = config.REDIS_STREAM_TO_IMAGE_HANDLER_NAME
    group_key = config.REDIS_IMAGE_HANDLER_GROUP_KEY
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
            new_image = image_processing(message_data=data)
            data[b'image'] = new_image
            r.xadd(config.REDIS_STREAM_TO_DB_SAVER_NAME, data)

        r.xack(stream_key, group_key, msg_id)
        r.xdel(stream_key, msg_id)

    logging.info("Waiting for new messages...")
    for msg in get_messages(r, block=0, count=1, streams={stream_key: '>'}):
        msg_id, data = msg
        new_image = image_processing(message_data=data)
        data[b'image'] = new_image
        r.xadd(config.REDIS_STREAM_TO_DB_SAVER_NAME, data)
        logging.info("The image has been sent to the db service")
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
