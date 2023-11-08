from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent import Agent
from schema import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = FastAPI()
agent = Agent()


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/dialogue")
async def dialogue(request: Message):
    response = agent.execute(request)
    return response


@app.get("/get_new_messages")
async def get_messages():
    response = agent.get_new_messages()
    return response


@app.post("/set_new_messages")
async def set_messages(name, message):
    response = agent.set_new_messages(name, message)
    return response


scheduler = AsyncIOScheduler()
scheduler.add_job(agent.get_live_chat, 'interval', seconds=10)
scheduler.start()



