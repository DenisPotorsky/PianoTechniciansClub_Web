from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
import urllib.request, urllib.parse, json

class CasesHandler:
    def __init__(self):
        self.api_base = "http://backend:8000/api/v1"
        self.web_base = "https://piano-technicians.club"
        self._tokens = {}  # кэш токенов: telegram_id -> token

    def _get_token(self, telegram_id: int) -> str | None:
        """Получить JWT токен для пользователя по telegram_id"""
        if telegram_id in self._tokens:
            return self._tokens[telegram_id]
        try:
            data = json.dumps({"telegram_id": telegram_id}).encode()
            req = urllib.request.Request(
                f"{self.api_base}/auth/whitelist-login",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            resp = urllib.request.urlopen(req, timeout=10)
            result = json.loads(resp.read())
            token = result.get("access_token")
            if token:
                self._tokens[telegram_id] = token
            return token
        except Exception as e:
            print(f"[CasesHandler] Ошибка авторизации tg_id={telegram_id}: {e}")
            return None

    def _api_get(self, path: str, token: str = None) -> dict | list:
        """GET запрос к API с авторизацией"""
        # Кодируем только query-параметры (после ?), путь оставляем как есть
        if '?' in path:
            base, qs = path.split('?', 1)
            # Перекодируем значения параметров
            pairs = urllib.parse.parse_qsl(qs)
            qs_encoded = urllib.parse.urlencode(pairs)
            url = f"{self.api_base}{base}?{qs_encoded}"
        else:
            url = f"{self.api_base}{path}"
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Поиск кейсов: /search <запрос>"""
        telegram_id = update.effective_user.id

        if not context.args:
            await update.message.reply_text(
                "🔍 *Поиск по базе знаний*\n\n"
                "Использование: `/search <симптом>`\n\n"
                "Примеры:\n"
                "• `/search клавиша западает`\n"
                "• `/search глухой звук`\n"
                "• `/search педаль не работает`",
                parse_mode="Markdown"
            )
            return

        token = self._get_token(telegram_id)
        if not token:
            await update.message.reply_text(
                "❌ У вас нет доступа к базе знаний.\n\n"
                "Зайдите на сайт и войдите через Telegram: "
                f"{self.web_base}"
            )
            return

        query = " ".join(context.args)

        try:
            params = urllib.parse.urlencode({"search": query, "limit": 5})
            data = self._api_get(f"/cases/?{params}", token=token)
            items = data.get("items", []) if isinstance(data, dict) else data

            if not items:
                await update.message.reply_text(
                    f"❌ По запросу «{query}» ничего не найдено.\n\n"
                    "Попробуйте другие слова или добавьте кейс через веб: "
                    f"{self.web_base}/cases/new"
                )
                return

            for case in items[:5]:
                symptoms = ", ".join(s["name"] for s in case.get("symptoms", []))
                tags = ", ".join(t["name"] for t in case.get("tags", []))
                solutions_count = case.get("solutions_count", 0)

                text = f"📚 *{case['title']}*\n\n"
                text += f"🔍 {(case.get('symptom_text') or 'Нет описания')[:150]}\n"
                if symptoms:
                    text += f"🔧 Симптомы: {symptoms}\n"
                if tags:
                    text += f"🏷 Теги: {tags}\n"
                text += f"💡 Решений: {solutions_count}\n"
                diff = {"easy": "🟢 Легко", "medium": "🟡 Средне", "hard": "🔴 Сложно"}
                text += f"⚙️ {diff.get(case.get('difficulty', ''), case.get('difficulty', ''))}"

                keyboard = [[InlineKeyboardButton(
                    "📖 Читать полностью",
                    url=f"{self.web_base}/cases/{case['id']}"
                )]]

                await update.message.reply_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

        except urllib.error.HTTPError as e:
            if e.code == 401:
                self._tokens.pop(telegram_id, None)
                await update.message.reply_text("❌ Сессия истекла. Попробуйте ещё раз.")
            else:
                await update.message.reply_text(f"❌ Ошибка поиска: {e}")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка поиска: {str(e)}")

    async def add_case_wizard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление кейса — перенаправление на веб"""
        keyboard = [[InlineKeyboardButton(
            "➕ Добавить кейс через веб",
            url=f"{self.web_base}/cases/new"
        )]]
        await update.message.reply_text(
            "➕ *Добавление нового кейса*\n\n"
            "Для удобного создания кейса используйте веб-интерфейс:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inline-режим: @bot <запрос> — поиск кейсов в любом чате"""
        telegram_id = update.effective_user.id
        query = update.inline_query.query.strip()

        if not query or len(query) < 2:
            await update.inline_query.answer([], cache_time=1)
            return

        token = self._get_token(telegram_id)
        items = []
        if token:
            try:
                params = urllib.parse.urlencode({"search": query, "limit": 10})
                data = self._api_get(f"/cases/?{params}", token=token)
                items = data.get("items", []) if isinstance(data, dict) else data
            except Exception:
                items = []

        articles = []
        for case in items[:10]:
            symptom_text = (case.get("symptom_text") or "")[:80]
            symptoms = ", ".join(s["name"] for s in case.get("symptoms", []))
            description = symptom_text or symptoms or "Нет описания"

            full_text = (
                f"📚 *{case['title']}*\n\n"
                f"🔍 {case.get('symptom_text', '')}\n"
            )
            if symptoms:
                full_text += f"🔧 {symptoms}\n"
            full_text += f"\n🔗 {self.web_base}/cases/{case['id']}"

            articles.append(InlineQueryResultArticle(
                id=str(case["id"]),
                title=case["title"],
                description=description,
                input_message_content=InputTextMessageContent(
                    full_text, parse_mode="Markdown"
                ),
                url=f"{self.web_base}/cases/{case['id']}",
            ))

        if not articles:
            articles.append(InlineQueryResultArticle(
                id="no_results",
                title="Ничего не найдено",
                description=f"По запросу «{query}» нет результатов",
                input_message_content=InputTextMessageContent(
                    f"❌ По запросу «{query}» ничего не найдено"
                ),
            ))

        await update.inline_query.answer(articles, cache_time=30)

    async def ai_assistant(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """AI-ассистент (пока fallback на обычный поиск)"""
        telegram_id = update.effective_user.id

        if not context.args:
            await update.message.reply_text(
                "🤖 *AI-ассистент*\n\n"
                "Опишите проблему, и я найду подходящие кейсы:\n"
                "`/ai клавиша не возвращается после нажатия`\n\n"
                "_Скоро здесь будет умный RAG-поиск!_",
                parse_mode="Markdown"
            )
            return

        query = " ".join(context.args)

        # Пробуем RAG-поиск (не требует авторизации для самого поиска)
        try:
            params = urllib.parse.urlencode({"q": query})
            token = self._get_token(telegram_id)
            if not token:
                await update.message.reply_text("❌ Нет доступа. Войдите на сайт: " + self.web_base)
                return
            rag_data = self._api_get(f"/ai/search?{params}", token=token)
            rag_results = rag_data.get("results", [])
        except Exception as e:
            print(f"[CasesHandler] RAG ошибка: {e}")
            rag_results = []

        if rag_results:
            response = f"🤖 *AI-поиск по запросу:* «{query}»\n\n"
            for i, r in enumerate(rag_results[:3], 1):
                score_pct = int(r.get("score", 0) * 100)
                response += (
                    f"*{i}. {r['title']}* (совпадение {score_pct}%)\n"
                    f"🔍 {r.get('symptom', '')[:100]}\n"
                )
                tags = ", ".join(r.get("tags", []))
                if tags:
                    response += f"🏷 {tags}\n"
                response += f"🔗 {self.web_base}/cases/{r['case_id']}\n\n"
            await update.message.reply_text(response, parse_mode="Markdown")
            return

        # Fallback: обычный поиск с авторизацией
        token = self._get_token(telegram_id)
        if not token:
            await update.message.reply_text(
                "❌ Нет доступа. Войдите на сайт: " + self.web_base
            )
            return

        try:
            params = urllib.parse.urlencode({"search": query, "limit": 3})
            data = self._api_get(f"/cases/?{params}", token=token)
            items = data.get("items", []) if isinstance(data, dict) else data
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
            return

        if not items:
            await update.message.reply_text(
                f"🤷 По запросу «{query}» ничего не найдено.\n\n"
                "Попробуйте описать проблему другими словами."
            )
            return

        response = f"🤖 *Найдено по запросу:* «{query}»\n\n"
        for i, case in enumerate(items[:3], 1):
            symptoms = ", ".join(s["name"] for s in case.get("symptoms", []))
            response += (
                f"*{i}. {case['title']}*\n"
                f"🔍 {(case.get('symptom_text') or 'Нет описания')[:100]}\n"
            )
            if symptoms:
                response += f"🔧 {symptoms}\n"
            response += f"🔗 {self.web_base}/cases/{case['id']}\n\n"

        await update.message.reply_text(response, parse_mode="Markdown")

    # ── CONVERSATION HANDLERS ──
    from telegram.ext import ConversationHandler, MessageHandler, filters

    WAITING_AI_QUERY = 1
    WAITING_SEARCH_QUERY = 2

    def get_ai_conversation_handler(self):
        """ConversationHandler для /ai — ждёт следующее сообщение как запрос"""
        async def ai_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if context.args:
                await self.ai_assistant(update, context)
                return ConversationHandler.END
            await update.message.reply_text(
                "🤖 *AI-ассистент*\n\n"
                "Опишите проблему — я найду подходящие кейсы:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🤖 Начать поиск", callback_data="ai_prompt")
                ]])
            )
            return self.WAITING_AI_QUERY

        async def ai_receive_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # Подделываем context.args из текста сообщения
            context.args = update.message.text.split()
            await self.ai_assistant(update, context)
            return ConversationHandler.END

        return ConversationHandler(
            entry_points=[CommandHandler("ai", ai_start)],
            states={
                self.WAITING_AI_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ai_receive_query)],
            },
            fallbacks=[],
        )

    def get_search_conversation_handler(self):
        """ConversationHandler для /search — ждёт следующее сообщение как запрос"""
        async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if context.args:
                await self.search(update, context)
                return ConversationHandler.END
            await update.message.reply_text(
                "🔍 *Поиск по базе знаний*\n\n"
                "Напишите симптом — я найду похожие кейсы:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔍 Найти симптом", callback_data="search_prompt")
                ]])
            )
            return self.WAITING_SEARCH_QUERY

        async def search_receive_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.args = update.message.text.split()
            await self.search(update, context)
            return ConversationHandler.END

        return ConversationHandler(
            entry_points=[CommandHandler("search", search_start)],
            states={
                self.WAITING_SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_receive_query)],
            },
            fallbacks=[],
        )
