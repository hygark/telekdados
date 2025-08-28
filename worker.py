import asyncio
import json
import random
import time
import os
from telethon import TelegramClient
from main import process_message, process_comments

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE = os.getenv('PHONE')
SOURCE = os.getenv('SOURCE_CHANNEL')
DEST = os.getenv('DEST_CHANNEL')
WORKER_ID = random.randint(1, 1000)

async def main():
    print(f"Worker {WORKER_ID} iniciado - Aguardando mensagens...")
    if not all([API_ID, API_HASH, PHONE, SOURCE, DEST]):
        print(f"Worker {WORKER_ID}: Variáveis de ambiente faltando!")
        return
    
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    client = TelegramClient(f'session_{WORKER_ID}', int(API_ID), API_HASH)
    await client.start(phone=PHONE)
    
    source_entity = await client.get_entity(SOURCE)
    dest_entity = await client.get_entity(DEST)
    
    while True:
        if random.random() < 0.05:
            print(f"Worker {WORKER_ID} reconectando (simulado)...")
            time.sleep(2)
            continue
        
        message_id = r.lpop('messages')
        if message_id:
            message_id = json.loads(message_id)['message_id']
            async for message in client.iter_messages(source_entity, ids=[message_id]):
                result = await process_message(client, source_entity, dest_entity, message, r)
                print(f"Worker {WORKER_ID} processou: {result}")
                comment_result = await process_comments(client, source_entity, dest_entity, message, r)
                if comment_result:
                    print(f"Worker {WORKER_ID} processou comentário: {comment_result}")
        time.sleep(1)
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())