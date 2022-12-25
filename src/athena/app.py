from telethon.sync import events


@events.register(events.NewMessage)
async def echo(event):
    await event.respond(event.raw_text)
