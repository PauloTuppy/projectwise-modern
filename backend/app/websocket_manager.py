from typing import Dict, List
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, document_id: str):
        await websocket.accept()
        if document_id not in self.connections:
            self.connections[document_id] = []
        self.connections[document_id].append(websocket)

    def disconnect(self, document_id: str, websocket: WebSocket):
        self.connections[document_id].remove(websocket)

    async def broadcast(self, document_id: str, data: dict):
        for connection in self.connections[document_id]:
            await connection.send_json(data)

manager = WebSocketManager()