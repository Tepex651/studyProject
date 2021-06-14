import asyncio
import aiofiles
import aiofiles.os
import enum


PROTOCOL = "РКСОК/1.0"
ENCODING = "UTF-8"

class ResponseStatus:
    """Response statuses specified in RKSOK specs for responses"""
    OK = "НОРМАЛДЫКС"
    NOTFOUND = "НИНАШОЛ"
    NOT_APPROVED = "НИЛЬЗЯ"
    INCORRECT_REQUEST = "НИПОНЯЛ"

class RequestAction(enum.Enum):
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

    async def _choosing_action(self) -> None:
        """Choosing action"""
        if self._action_from_request == RequestAction.WRITE.value:
            await self._write()
        elif self._action_from_request == RequestAction.GET.value:
            await self._get()
        elif self._action_from_request == RequestAction.DELETE.value:
            await self._delete()
        else:
            self._status_for_response = ResponseStatus.INCORRECT_REQUEST
            
    async def compose_response(self) -> bytes:
        """Makes response. Checks answer from server verification and protocol"""  
        if self._status_for_response != ResponseStatus.INCORRECT_REQUEST:
            await self._choosing_action()
        response = f'{self._status_for_response} {PROTOCOL}'
        if self._phone_for_response:
            response += f'\r\n{self._phone_for_response}'
        response += '\r\n\r\n'
        return response.encode(ENCODING)

    def is_correct_request(self) -> bool:
        """Checks protocol in request and action in class RequestAction. Starts parse_request function"""
        if PROTOCOL in self._request:
            self._parse_request()
            if self._action_from_request in [verb.value for verb in RequestAction]:
                return True
        else:
            self._status_for_response = ResponseStatus.INCORRECT_REQUEST
            return False

    async def ask_server_verification(self) -> bytes:
        """Asks the verification server for the possibility of executing the request"""
        reader, writer = await asyncio.open_connection('vragi-vezde.to.digital', 51624)
        question = f"АМОЖНА? {PROTOCOL}\r\n".encode(ENCODING) + self._request.encode(ENCODING)
        writer.write(question)
        answer = await reader.read(200)
        writer.close()
        return answer

    def _parse_request(self) -> None:
        """Parses request. Sets action, name and phone from request"""
        action_and_name_from_request = self._request.split(PROTOCOL)
        self._action_from_request = action_and_name_from_request[0].split()[0]
        self._name_from_request = ' '.join(action_and_name_from_request[0].split()[1:])
        self._phone_from_request = self._request.split('\r\n')[1]

    async def _write(self) -> None:
        """Create new file with name from request. Writes phone inside. Sets status"""
        try:
            async with aiofiles.open(f'phonebook/{self._name_from_request}.txt', 'w') as f:
                await f.write(self._phone_from_request)
                self._status_for_response = ResponseStatus.OK
        except Exception:
            self._status_for_response = ResponseStatus.INCORRECT_REQUEST

    async def _get(self) -> None:
        """Finds file for name and set status"""
        try:
            async with aiofiles.open(f'phonebook/{self._name_from_request}.txt', 'r') as f:
                self._phone_for_response = await f.read()
                self._status_for_response = ResponseStatus.OK
        except FileNotFoundError:
            self._status_for_response = ResponseStatus.NOTFOUND
        except Exception:
            self._status_for_response = ResponseStatus.INCORRECT_REQUEST

    async def _delete(self) -> None:
        """Removes file for name and set status"""
        try:
            await aiofiles.os.remove(f'phonebook/{self._name_from_request}.txt')
            self._status_for_response = ResponseStatus.OK
        except FileNotFoundError:
            self._status_for_response = ResponseStatus.NOTFOUND
        except Exception:
            self._status_for_response = ResponseStatus.INCORRECT_REQUEST