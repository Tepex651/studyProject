import asyncio
import os

from loguru import logger

from models import ServerRKSOK, ENCODING, ResponseStatus


logger.add('file.log', format='{time} {level} {message}', enqueue=True)

async def proccess(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Creates a server object, receives a request, and sends a response"""
    if not os.path.exists('phonebook'):
        os.mkdir('phonebook')
    request = await reader.read(200)
    logger.info(f'Request = {request.decode(ENCODING)!r}')
    server = ServerRKSOK(request)
    if server.is_correct_request():
        answer_from_server_verification = await server.ask_server_verification()
        if answer_from_server_verification.decode(ENCODING).startswith(ResponseStatus.NOT_APPROVED):
            response = answer_from_server_verification + b"\r\n"
        else:
            response = await server.compose_response()
    else:
        response = await server.compose_response()
    logger.info(f'Response = {response.decode(ENCODING)!r}')
    writer.write(response)
    writer.close()


async def main() -> None:
    """Starts the server and waits for a connection"""
    start_server = await asyncio.start_server(proccess, '', 8000)
    async with start_server:
        await start_server.serve_forever()