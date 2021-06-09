from admin.OrderHandler import OrderHandler as orderHandler
import websockets
import asyncio
from admin import *
import json
import logging
class AdminController:
    async def control(self, websocket, path):
        async for message in websocket:
            method = json.loads(message)['method']
            logging.info('method: ' + method)
            if method == 'createOrder' or method == 'fetchOrders' or method == 'finishOrder':
                await self.setOrderHandler(message)
            elif method == 'getBill':
                pass
            elif method == 'getDetailedList':
                pass
            elif method == 'getStatistics':
                pass
            elif method == 'getSystemStatus':
                pass
            elif method == 'startSystem':
                pass
            elif method == 'stopSystem':
                pass
            elif method == 'getSysConfig':
                pass
            elif method == 'setSysConfig':
                pass
            else:
                pass
            
    async def serve(self):
        await websockets.serve(self.control, '127.0.0.1', 8765)

    async def setOrderHandler(self, message):
        await orderHandler(message).run()