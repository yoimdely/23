from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from ..config import Settings
from ..services.analytics import AnalyticsService
from ..services.storage import StorageService
from .documents import build_documents_keyboard
from .middleware import DependencyMiddleware

router = Router()


def setup_router(settings: Settings, analytics: AnalyticsService, storage: StorageService) -> Router:
    router.message.middleware(
        DependencyMiddleware(settings=settings, analytics=analytics, storage=storage)
    )
    return router


@router.message(CommandStart())
async def cmd_start(message: Message, settings: Settings, analytics: AnalyticsService) -> None:
    analytics.log_event("start", message.from_user.id, {})
    await message.answer(
        "Привет! Я CLEAN DOC BOT — генератор юридических документов. Выберите документ для начала:",
        reply_markup=build_documents_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "1) Выберите документ.\n"
        "2) Ответьте на вопросы.\n"
        "3) Получите PDF.\n"
        "Доступны бесплатные и Pro-подписки."
    )


@router.message(Command("docs"))
async def cmd_docs(message: Message) -> None:
    await message.answer("Доступные шаблоны:", reply_markup=build_documents_keyboard())


@router.message(Command("profile"))
async def cmd_profile(message: Message, storage: StorageService) -> None:
    profile = storage.get_profile(message.from_user.id)
    await message.answer(
        f"Ваш профиль:\nПодписка: {'Pro' if profile.is_pro else 'Free'}\n"
        f"Сгенерировано сегодня: {profile.documents_generated}\n"
        f"История: {', '.join(profile.history or []) if profile.history else 'нет'}"
    )
