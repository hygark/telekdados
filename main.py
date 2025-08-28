import asyncio
import json
import random
import time
from telethon import TelegramClient
import redis
from grafana_api.grafana_face import GrafanaFace
import boto3

# Configurações
REDIS_HOST = 'redis'
GRAFANA_URL = 'http://grafana:3000'
RATE_LIMIT_DELAY = 1

async def process_message(client, source, dest, message, r):
    result = {'message_id': message.id, 'type': 'unknown', 'status': 'failed', 'data': None}
    
    try:
        if random.random() < 0.05:
            result['data'] = 'Worker failed (simulated)'
            return result
        
        if message.text:
            result['type'] = 'text'
            await client.send_message(dest, message.text)
            result['status'] = 'success'
            result['data'] = 'Text copied'
        
        elif message.photo:
            result['type'] = 'photo'
            file = await client.download_media(message.photo, file=f'photo_{message.id}.jpg')
            await client.send_file(dest, file)
            result['status'] = 'success'
            result['data'] = 'Photo copied'
        
        elif message.video:
            result['type'] = 'video'
            file = await client.download_media(message.video, file=f'video_{message.id}.mp4')
            await client.send_file(dest, file)
            result['status'] = 'success'
            result['data'] = 'Video copied'
        
        elif message.document:
            result['type'] = 'document'
            file = await client.download_media(message.document, file=f'doc_{message.id}')
            await client.send_file(dest, file)
            result['status'] = 'success'
            result['data'] = 'Document copied'
        
        elif message.audio:
            result['type'] = 'audio'
            file = await client.download_media(message.audio, file=f'audio_{message.id}.mp3')
            await client.send_file(dest, file)
            result['status'] = 'success'
            result['data'] = 'Audio copied'
        
        time.sleep(RATE_LIMIT_DELAY)
    
    except Exception as e:
        result['data'] = str(e)
    
    return result

async def process_comments(client, source, dest, message, r):
    if message.is_channel and message.post:
        try:
            comments = await client.get_messages(source, reply_to=message.id, limit=50)
            for comment in comments:
                result = {'message_id': comment.id, 'type': 'comment', 'status': 'failed', 'data': None}
                if random.random() < 0.05:
                    result['data'] = 'Worker failed (simulated)'
                    return result
                if comment.text:
                    await client.send_message(dest, f"Comment on post {message.id}: {comment.text}")
                    result['status'] = 'success'
                    result['data'] = 'Comment copied'
                time.sleep(RATE_LIMIT_DELAY)
                return result
        except:
            return None
    return None

def integrate_with_cloud(data):
    s3 = boto3.client('s3')
    bucket = 'seu-bucket-autorizado'
    s3.put_object(Bucket=bucket, Key='telekdados_data.json', Body=json.dumps(data))
    print("Dados enviados para AWS S3.")

def create_grafana_dashboard(api_key, data):
    grafana = GrafanaFace(auth=api_key, host=GRAFANA_URL.replace('http://', ''))
    dashboard = {
        "dashboard": {
            "id": None,
            "uid": None,
            "title": "Hygark's TelekDados Dashboard",
            "panels": [{
                "id": 1,
                "title": "Backup Results",
                "type": "graph",
                "targets": [{
                    "refId": "A",
                    "target": "telekdados_results"
                }],
                "datasource": "Prometheus"
            }],
            "schemaVersion": 30
        },
        "folderId": 0,
        "overwrite": True
    }
    grafana.dashboard.create_or_update_dashboard(dashboard)
    print("Dashboard criado no Grafana!")

def generate_chart(data):
    labels = [f"Message {d['message_id']}" for d in data]
    values = [1 if d['status'] == 'success' else 0 for d in data]
    types = [d['type'] for d in data]
    
    chart_data = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Status (1=Success, 0=Failed)",
                    "data": values,
                    "backgroundColor": ["#1f77b4" if v == 1 else "#ff7f0e" for v in values],
                    "borderColor": ["#1f77b4" if v == 1 else "#ff7f0e" for v in values],
                    "borderWidth": 1
                },
                {
                    "label": "Content Type",
                    "data": [1 if t != 'unknown' else 0 for t in types],
                    "type": "line",
                    "borderColor": "#2ca02c",
                    "fill": False
                }
            ]
        },
        "options": {
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "max": 1
                }
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Hygark's TelekDados Results (Messages and Comments)"
                }
            }
        }
    }
    
    with open('chart.html', 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Hygark's TelekDados Chart</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <canvas id="myChart" style="max-width: 800px;"></canvas>
            <script>
                const ctx = document.getElementById('myChart').getContext('2d');
                new Chart(ctx, %s);
            </script>
        </body>
        </html>
        """ % json.dumps(chart_data))
    print("Gráfico interativo salvo em chart.html")

async def main(source, dest, api_id, api_hash, phone, grafana_key):
    print("Iniciando Hygark's TelekDados - SIMULAÇÃO APENAS!")
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    
    client = TelegramClient('session', int(api_id), api_hash)
    await client.start(phone=phone)
    
    source_entity = await client.get_entity(source)
    dest_entity = await client.get_entity(dest)
    
    # Enviar mensagens pra Redis
    async for message in client.iter_messages(source_entity, limit=100):
        r.rpush('messages', json.dumps({'message_id': message.id}))
    
    # Processar mensagens
    results = []
    async for message in client.iter_messages(source_entity, limit=100):
        result = await process_message(client, source_entity, dest_entity, message, r)
        results.append(result)
        comment_result = await process_comments(client, source_entity, dest_entity, message, r)
        if comment_result:
            results.append(comment_result)
    
    # Exportar
    with open('output.json', 'w') as f:
        json.dump(results, f)
    print("Dados salvos em output.json")
    
    # Gráfico
    generate_chart(results)
    
    # Grafana
    if grafana_key:
        create_grafana_dashboard(grafana_key, results)
    
    # Opcional: AWS
    # integrate_with_cloud(results)
    
    await client.disconnect()