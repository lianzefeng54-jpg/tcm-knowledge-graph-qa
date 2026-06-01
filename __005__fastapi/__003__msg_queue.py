import asyncio


# 键 设置成user_id, 值

class MsgQueueManager:
    def __init__(self):
        self.msg_queue_dict = {}

    def get_msg_queue(self, user_id):
        if user_id not in self.msg_queue_dict:
            self.msg_queue_dict[user_id] = asyncio.Queue()
        return self.msg_queue_dict[user_id]

    def del_msg_queue(self, user_id):
        if user_id in self.msg_queue_dict:
            del self.msg_queue_dict[user_id]


msg_queue_manager = MsgQueueManager()


async def put_msg_content(user_id, put_content):
    await msg_queue_manager.get_msg_queue(user_id).put({"type": "msg", "msg": put_content})
    await asyncio.sleep(0.1)


async def put_msg_sentence_content(user_id, put_content):
    await msg_queue_manager.get_msg_queue(user_id).put({"type": "msg", "msg": put_content})
    await msg_queue_manager.get_msg_queue(user_id).put({"type": "msg", "msg": "\n"})
    await asyncio.sleep(0.1)


async def put_reply_content(user_id, put_content):
    await msg_queue_manager.get_msg_queue(user_id).put({"type": "reply", "msg": put_content})
    await asyncio.sleep(0.1)


async def put_done_content(user_id):
    await msg_queue_manager.get_msg_queue(user_id).put({"type": "done", "msg": ""})
    await asyncio.sleep(0.1)


def remove_msg_queue(user_id):
    msg_queue_manager.del_msg_queue(user_id)
