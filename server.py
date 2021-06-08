from os import read
import asyncio
import aiofiles



PROTOCOL = "РКСОК/1.0"
ENCODING = "UTF-8"

class ResponseStatus:
    """Response statuses specified in RKSOK specs for responses"""
    OK = "НОРМАЛДЫКС"
    NOTFOUND = "НИНАШОЛ"
    NOT_APPROVED = "НИЛЬЗЯ"
    INCORRECT_REQUEST = "НИПОНЯЛ"

class RequestVerb:
    """Verbs specified in RKSOK specs for requests"""
    GET = "ОТДОВАЙ"
    DELETE = "УДОЛИ"
    WRITE = "ЗОПИШИ"


class ServerRKSOK:
    def __init__(self, request: bytes) -> None:
        self._request = request.decode(ENCODING)
        self._action_from_request, self._name_from_request, self._phone_from_request = None, None, None
        self._status, self._response = None, None

    def _compose_response(self):
        self._parse_request()
        if self._action_from_request == RequestVerb.WRITE:
            self._write()

        print(f"{self._status} {PROTOCOL}")
        pass 


    def _parse_request(self):
        action_and_name_from_request = self._request.split(PROTOCOL)
        self._action_from_request = action_and_name_from_request[0].split()[0]
        self._name_from_request = ' '.join(action_and_name_from_request[0].split()[1:])
        self._phone_from_request = self._request.split('\r\n')[1]
        print('self._action_from_request=', self._action_from_request)
        print('self._name_from_request=', self._name_from_request)
        print('self._phone_from_request=', self._phone_from_request)

    async def _write(self):
        try:
            async with aiofiles.open(f'phonebook/{self._name_from_request}', 'w') as f:
                f.write(self._phone_from_request)
                self._status = ResponseStatus.OK
        except Exception:
            self._status = ResponseStatus.NOT_APPROVED



async def proccess(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    request = await reader.read(100)
    response = ServerRKSOK(request)
    response._compose_response()
    message = request.decode(ENCODING)
    print(f"Received {message!r}")

    # print(f"Send: {message!r}")
    # writer.write(input_data)
    # await writer.drain()

    # pass 


async def main():
    server = await asyncio.start_server(proccess, '', 8000)
    async with server:
        await server.serve_forever()

asyncio.run(main())






















# class ServerRKSOK:
#     def __init__(self, port: int) -> None:
#         self._port = port
#         self._name, self._phone, self._action = None
#         self._request, self._response = None

    
#     def proccess(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        
#         pass

#     def get_request(self, ):
#         pass


# async def main():
#     server = ServerRKSOK(8000)
