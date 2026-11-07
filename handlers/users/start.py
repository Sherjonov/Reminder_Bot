"""/start, salomlashuv va botni bloklash/blokdan chiqarishni kuzatish."""
from aiogram import F, Router
from aiogram.filters import KICKED, MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated, Message

from filters import private_only
from services.db_api import users as user_db
from services.welcome import send_welcome

router = Router(name="user_start")
private_only(router)
router.my_chat_member.filter(F.chat.type == "private")


async def show_start(message: Message, db_user: dict, lang: str) -> None:
    await send_welcome(message, message.from_user.first_name or "👋", lang)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER >> KICKED))
async def on_blocked(event: ChatMemberUpdated) -> None:
    await user_db.set_blocked(event.from_user.id, True)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED >> MEMBER))
async def on_unblocked(event: ChatMemberUpdated) -> None:
    await user_db.set_blocked(event.from_user.id, False)
