from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..config import Settings
from ..services.analytics import AnalyticsService
from ..services.pdf_builder import PdfBuilder
from ..services.storage import StorageService
from ..services.templates_loader import TemplateLoader
from .middleware import DependencyMiddleware


documents_router = Router()


@dataclass
class DocumentDefinition:
    code: str
    title: str
    template: str
    questions: List[str]


DOCUMENTS: List[DocumentDefinition] = [
    DocumentDefinition(
        code="dkp_goods",
        title="ДКП товара",
        template="dkp_template.jinja",
        questions=[
            "ФИО продавца",
            "Паспортные данные продавца",
            "Адрес регистрации продавца",
            "ФИО покупателя",
            "Паспортные данные покупателя",
            "Адрес покупателя",
            "Предмет договора",
            "Состояние товара",
            "Цена",
            "Место сделки",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="dkp_car",
        title="ДКП автомобиля",
        template="dkp_car_template.jinja",
        questions=[
            "ФИО продавца",
            "Паспорт продавца",
            "ФИО покупателя",
            "Паспорт покупателя",
            "Марка и модель",
            "VIN",
            "Год выпуска",
            "Пробег",
            "Цена",
            "Город сделки",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="dkp_property",
        title="ДКП недвижимости",
        template="dkp_property_template.jinja",
        questions=[
            "ФИО продавца",
            "Паспорт продавца",
            "ФИО покупателя",
            "Паспорт покупателя",
            "Адрес объекта",
            "Кадастровый номер",
            "Площадь",
            "Цена",
            "Порядок расчетов",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="rent_flat",
        title="Договор аренды квартиры",
        template="rent_template.jinja",
        questions=[
            "ФИО арендодателя",
            "Паспорт арендодателя",
            "ФИО арендатора",
            "Паспорт арендатора",
            "Адрес квартиры",
            "Срок аренды",
            "Арендная плата",
            "Размер залога",
            "Условия коммунальных платежей",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="rent_room",
        title="Договор аренды комнаты",
        template="rent_room_template.jinja",
        questions=[
            "ФИО арендодателя",
            "Паспорт арендодателя",
            "ФИО арендатора",
            "Паспорт арендатора",
            "Адрес комнаты",
            "Срок аренды",
            "Арендная плата",
            "Порядок оплаты",
            "Правила проживания",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="rent_car",
        title="Договор аренды автомобиля",
        template="rent_car_template.jinja",
        questions=[
            "ФИО арендодателя",
            "Паспорт арендодателя",
            "ФИО арендатора",
            "Паспорт арендатора",
            "Марка, модель",
            "Регистрационный номер",
            "Срок аренды",
            "Стоимость аренды",
            "Лимит пробега",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="service_contract",
        title="Договор оказания услуг",
        template="service_contract_template.jinja",
        questions=[
            "ФИО исполнителя",
            "ФИО заказчика",
            "Описание услуги",
            "Стоимость",
            "Срок исполнения",
            "Порядок оплаты",
            "Ответственность",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="contractor",
        title="Договор подряда",
        template="contractor_template.jinja",
        questions=[
            "Подрядчик",
            "Заказчик",
            "Предмет работ",
            "Стоимость работ",
            "Сроки выполнения",
            "Порядок оплаты",
            "Гарантии",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="photography",
        title="Договор на фотографа",
        template="photography_template.jinja",
        questions=[
            "Фотограф",
            "Клиент",
            "Место съемки",
            "Дата и время",
            "Количество часов",
            "Стоимость",
            "Передача материалов",
            "Дата договора",
        ],
    ),
    DocumentDefinition(
        code="realtor",
        title="Договор риэлторских услуг",
        template="realtor_template.jinja",
        questions=[
            "Риэлтор",
            "Клиент",
            "Объект сопровождения",
            "Вознаграждение",
            "Срок действия",
            "Обязанности",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="household",
        title="Договор бытового подряда",
        template="household_template.jinja",
        questions=[
            "Исполнитель",
            "Заказчик",
            "Вид работ",
            "Стоимость",
            "Срок выполнения",
            "Материалы",
            "Гарантийный срок",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="receipt_money",
        title="Расписка о передаче денег",
        template="receipt_template.jinja",
        questions=[
            "ФИО получателя",
            "Паспорт получателя",
            "Сумма",
            "ФИО передающего",
            "Основание передачи",
            "Дата передачи",
            "Город",
        ],
    ),
    DocumentDefinition(
        code="receipt_deposit",
        title="Расписка о задатке",
        template="receipt_deposit_template.jinja",
        questions=[
            "ФИО сторон",
            "Сумма задатка",
            "Основание",
            "Дата",
            "Город",
        ],
    ),
    DocumentDefinition(
        code="power_of_attorney",
        title="Доверенность",
        template="power_of_attorney_template.jinja",
        questions=[
            "Доверитель",
            "Паспорт доверителя",
            "Представитель",
            "Паспорт представителя",
            "Полномочия",
            "Срок действия",
            "Город",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="handover",
        title="Акт приема-передачи",
        template="handover_template.jinja",
        questions=[
            "Сторона 1",
            "Сторона 2",
            "Предмет передачи",
            "Состояние",
            "Количество",
            "Место",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="work_completion",
        title="Акт выполненных работ",
        template="work_completion_template.jinja",
        questions=[
            "Исполнитель",
            "Заказчик",
            "Вид работ",
            "Результат",
            "Стоимость",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="refund_agreement",
        title="Соглашение о возврате денег",
        template="refund_agreement_template.jinja",
        questions=[
            "Кредитор",
            "Должник",
            "Сумма возврата",
            "Срок",
            "Порядок платежа",
            "Город",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="claim_seller",
        title="Претензия продавцу",
        template="claim_seller_template.jinja",
        questions=[
            "Покупатель",
            "Продавец",
            "Товар",
            "Недостаток",
            "Требование",
            "Дата покупки",
            "Город",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="claim_renter",
        title="Претензия арендатору",
        template="claim_renter_template.jinja",
        questions=[
            "Арендодатель",
            "Арендатор",
            "Адрес помещения",
            "Нарушение",
            "Требование",
            "Срок исполнения",
            "Дата",
        ],
    ),
    DocumentDefinition(
        code="consent_personal",
        title="Согласие на обработку ПДн",
        template="consent_personal_template.jinja",
        questions=[
            "ФИО субъекта",
            "Паспорт",
            "Адрес",
            "Цель обработки",
            "Срок хранения",
            "Дата",
            "Город",
        ],
    ),
]


class DocumentForm(StatesGroup):
    choosing_document = State()
    collecting_data = State()
    confirming = State()


def build_documents_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=doc.title, callback_data=f"doc:{doc.code}")] for doc in DOCUMENTS
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def setup_router(settings: Settings, analytics: AnalyticsService, storage: StorageService) -> Router:
    documents_router.message.middleware(
        DependencyMiddleware(settings=settings, analytics=analytics, storage=storage)
    )
    documents_router.callback_query.middleware(
        DependencyMiddleware(settings=settings, analytics=analytics, storage=storage)
    )
    return documents_router


@documents_router.callback_query(F.data.startswith("doc:"))
async def start_document(
    callback: CallbackQuery, state: FSMContext, analytics: AnalyticsService, storage: StorageService
) -> None:
    code = callback.data.split(":", maxsplit=1)[1]
    await state.set_state(DocumentForm.collecting_data)
    await state.update_data(document_code=code, answers=[], index=0)
    await callback.answer()
    await callback.message.answer("Начинаем заполнять документ. Отвечайте на вопросы. Для отмены введите /cancel.")
    await ask_next_question(callback.message, state, storage, analytics)
    analytics.log_event("document_selected", callback.from_user.id, {"document": code})


async def ask_next_question(
    message: Message, state: FSMContext, storage: StorageService, analytics: AnalyticsService
) -> None:
    data = await state.get_data()
    document = next(doc for doc in DOCUMENTS if doc.code == data["document_code"])
    index = data.get("index", 0)
    if index >= len(document.questions):
        await state.set_state(DocumentForm.confirming)
        await message.answer("Спасибо! Формирую документ...")
        await finalize_document(message, state, storage, analytics)
        return
    question = document.questions[index]
    await message.answer(f"{question}\nВведите ответ или /back для возврата.")


@documents_router.message(Command("cancel"))
async def cancel_creation(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Создание документа отменено. Чтобы начать снова, выберите документ из списка.")


@documents_router.message(Command("back"))
async def go_back(message: Message, state: FSMContext, storage: StorageService, analytics: AnalyticsService) -> None:
    data = await state.get_data()
    index = max(0, data.get("index", 0) - 1)
    await state.update_data(index=index)
    await ask_next_question(message, state, storage, analytics)


@documents_router.message(DocumentForm.collecting_data)
async def collect_data(
    message: Message, state: FSMContext, storage: StorageService, analytics: AnalyticsService
) -> None:
    if not storage.can_generate(message.from_user.id):
        await message.answer("Достигнут лимит генераций на сегодня. Оформите Pro, чтобы продолжить.")
        return
    data = await state.get_data()
    answers: List[str] = data.get("answers", [])
    answers.append(message.text)
    index = data.get("index", 0) + 1
    await state.update_data(answers=answers, index=index)
    await ask_next_question(message, state, storage, analytics)


async def finalize_document(
    message: Message, state: FSMContext, storage: StorageService, analytics: AnalyticsService
) -> None:
    data = await state.get_data()
    document = next(doc for doc in DOCUMENTS if doc.code == data["document_code"])
    context = {f"field_{i+1}": answer for i, answer in enumerate(data.get("answers", []))}
    template_loader = TemplateLoader(Path(__file__).resolve().parent.parent / "data" / "templates")
    pdf_builder = PdfBuilder(template_loader)
    pdf_file = pdf_builder.build(document.template, context)
    storage.register_generation(message.from_user.id, document.title)
    analytics.log_event("document_generated", message.from_user.id, {"document": document.title})

    await message.answer_document(pdf_file, filename=f"{document.code}.pdf")
    await message.answer(
        "Документ готов! Что дальше?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Сгенерировать другой документ", callback_data="docs")],
                [InlineKeyboardButton(text="Скачать DOCX (скоро)", callback_data="docx_placeholder")],
                [InlineKeyboardButton(text="Оформить подписку Pro", callback_data="upgrade")],
            ]
        ),
    )
    await state.clear()


@documents_router.callback_query(F.data == "docs")
async def show_docs(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("Список документов:", reply_markup=build_documents_keyboard())


@documents_router.callback_query(F.data == "docx_placeholder")
async def docx_placeholder(callback: CallbackQuery) -> None:
    await callback.answer("DOCX версия в разработке", show_alert=True)


@documents_router.callback_query(F.data == "upgrade")
async def upgrade_placeholder(callback: CallbackQuery) -> None:
    await callback.answer("Оформление Pro скоро будет доступно", show_alert=True)
