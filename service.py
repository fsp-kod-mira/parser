from parser import Parser
import json
from cv import CV
from nats.aio.msg import Msg
from nats.js import JetStreamContext


class Service:
    def __init__(self, parser: Parser, js: JetStreamContext):
        self.parser = parser
        self.js = js

    async def parser_handler(self, msg: Msg):
        subject = msg.subject
        data = msg.data.decode()
        try:
            json_data = json.loads(data)
            cv_id = json_data.get("cvId")
            text = json_data.get("text")
            print(
                f"Received a message on '{subject}': cvId={cv_id}, text={text}")
            new_cv = CV(cv_id, text)
            await self.parse_cv(new_cv)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from message on '{subject}': {data}")
        await msg.ack()  # Подтверждение получения сообщения

    async def parse_cv(self, cv: CV):
        name = await self.parser.extract_name(cv.text)
        await self.pub(cv.id, "creds", name)
        phone = await self.parser.extract_phone(cv.text)
        await self.pub(cv.id, "phone", phone)
        email = await self.parser.extract_email(cv.text)
        await self.pub(cv.id, "email", email)
        birthdate = await self.parser.extract_date_of_birth(cv.text)
        await self.pub(cv.id, "birthdate", birthdate)
        living = await self.parser.extract_living(cv.text)
        await self.pub(cv.id, "birthdate", living)
        skills = await self.parser.extract_skills(cv.text)
        await self.pub(cv.id, "skills", skills)

        works = await self.parser.extract_work(cv.text)
        for work in works:
            await self.pub(cv.id, "work", work)

    async def pub(self, cv_id, field, data: str):
        print(data)
        if data is None or len(data) < 1:
            return

        json_data = {
            "cvId": cv_id,
            "field": field,
            "data": data,
        }
        message = json.dumps(json_data)
        await self.js.publish("cv.feature", message.encode())
        print(f"Published message to cv.feature: {message}")
