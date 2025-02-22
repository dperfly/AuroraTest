import asyncio
import websockets


# 定义一个处理 WebSocket 连接的函数
async def handle_connection(websocket):  # 去掉 path 参数
    print("新的客户端连接")
    try:
        async for message in websocket:
            print(f"收到消息: {message}")
            # 将消息原样返回给客户端
            await websocket.send(f"服务器收到: {message}")
            # 返回第 1 条数据
            await websocket.send(f"服务器返回的第 1 条数据: {message}")
            # 返回第 2 条数据
            await websocket.send(f"服务器返回的第 2 条数据: {message.upper()}")
            await asyncio.sleep(1)  # 模拟延迟（可选）

            # 返回第 3 条数据
            await websocket.send(f"服务器返回的第 3 条数据: {message[::-1]}")
    except websockets.ConnectionClosed:
        print("客户端断开连接")


# 启动 WebSocket 服务器
async def start_server():
    print("WebSocket 服务器已启动，监听端口 8765")
    async with websockets.serve(handle_connection, "localhost", 8765):
        await asyncio.Future()  # 永久运行


# 运行事件循环
if __name__ == "__main__":
    asyncio.run(start_server())
