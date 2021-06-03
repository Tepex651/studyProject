import asyncio
import aiofiles
import aiofiles.os



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
    """It is Server RKSOK. He can write, delete and find files from phonebook"""

    def __init__(self, request: bytes) -> None:
        self._request = request.decode(ENCODING)
        self._action_from_request, self._name_from_request, self._phone_from_request = None, None, None
        self._status_for_response, self._phone_for_response = None, None

    async def _choosing_action(self):
        """Choosing action"""
        self._parse_request()
        if self._action_from_request == RequestVerb.WRITE:
            await self._write()
        elif self._action_from_request == RequestVerb.GET:
            await self._get()
        elif self._action_from_request == RequestVerb.DELETE:
            await self._delete()
        else:
            self._status_for_response = ResponseStatus.INCORRECT_REQUEST
            
    async def _compose_response(self) -> bytes:
        """Makes response"""
        await self._choosing_action()
        response = f'{self._status_for_response} {PROTOCOL}'
        if self._phone_for_response:
            response += f'\r\n{self._phone_for_response}'
        response += '\r\n\r\n'
        return response.encode(ENCODING)

    def _parse_request(self):
        """Parses request. Sets action, name and phone from request"""
        action_and_name_from_request = self._request.split(PROTOCOL)
        self._action_from_request = action_and_name_from_request[0].split()[0]
        self._name_from_request = ' '.join(action_and_name_from_request[0].split()[1:])
        self._phone_from_request = self._request.split('\r\n')[1]

    async def _write(self):
        """Create new file with name from request. Writes phone inside. Sets status"""
        print('ServerRKSOK._WRITE started')
        try:
            async with aiofiles.open(f'phonebook/{self._name_from_request}.txt', 'w') as f:
                await f.write(self._phone_from_request)
                self._status_for_response = ResponseStatus.OK
        except Exception as e:
            self._status_for_response = ResponseStatus.INCORRECT_REQUEST

    async def _get(self):
        """Finds file for name and set status"""
        try:
            async with aiofiles.open(f'phonebook/{self._name_from_request}.txt', 'r') as f:
                self._phone_for_response = await f.read()
                self._status_for_response = ResponseStatus.OK
        except FileNotFoundError:
            self._status_for_response = ResponseStatus.NOTFOUND
        except Exception:
            self._status_for_response = ResponseStatus.INCORRECT_REQUEST

    async def _delete(self):
        """Removes file for name and set status"""
        try:
            await aiofiles.os.remove(f'phonebook/{self._name_from_request}.txt')
            self._status_for_response = ResponseStatus.OK
        except FileNotFoundError:
            self._status_for_response = ResponseStatus.NOTFOUND
        except Exception:
            self._status_for_response = ResponseStatus.INCORRECT_REQUEST

async def proccess(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    request = await reader.read(100)
    server = ServerRKSOK(request)
    response = await server._compose_response()
    print(f"Received {request.decode(ENCODING)!r}")
    print(f"Send: {response.decode(ENCODING)!r}")
    writer.write(response)
    await writer.drain()
    print("Close the connection")
    # writer.close()


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
