"""Hermes Dev Assistant — Main entry point.

A Developer Productivity Assistant that monitors GitHub issues,
summarizes daily code activity, drafts standup reports, tracks tasks
via Notion, and responds through Telegram.
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Load environment before importing project modules
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.dev_workflow import DevWorkflow  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from typing import Optional  # noqa: E402

# Initialize workflow (lazy — created on first message)
_workflow: Optional[DevWorkflow] = None


def get_workflow() -> DevWorkflow:
    """Lazily initialize the workflow router."""
    global _workflow
    if _workflow is None:
        _workflow = DevWorkflow()
    return _workflow


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    welcome = (
        "👋 **Hermes Dev Assistant** is ready!\n\n"
        "I can help you with:\n"
        "• `/standup` — Generate your daily standup report\n"
        "• `/issues` — Summarize open GitHub issues\n"
        "• `/tasks` — List your Notion tasks\n"
        "• `/plan` — Create a prioritized daily plan\n"
        "• `/weekly` — Generate weekly summary\n"
        "• `set repo owner/name` — Set default GitHub repo\n\n"
        "Or just send me a message and I'll figure out how to help!"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = (
        "**Available Commands:**\n\n"
        "`/standup` — Daily standup report\n"
        "`/issues` — GitHub issue summary\n"
        "`/tasks` — List Notion tasks\n"
        "`/plan` — Prioritized daily plan\n"
        "`/weekly` — Weekly summary report\n"
        "`/addtask <title>` — Add task to Notion\n"
        "`/setrepo <owner/repo>` — Set default repo\n\n"
        "**Natural Language:**\n"
        "You can also just type naturally:\n"
        "• \"What are my open issues?\"\n"
        "• \"Generate my standup\"\n"
        "• \"Extract tasks from: <meeting notes>\"\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def standup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /standup command."""
    await update.message.reply_text("Generating standup report... ⏳")
    workflow = get_workflow()
    response = workflow.handle("generate my standup report")
    await update.message.reply_text(response, parse_mode="Markdown")


async def issues_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /issues command."""
    workflow = get_workflow()
    response = workflow.handle("show my github issues")
    await update.message.reply_text(response, parse_mode="Markdown")


async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tasks command."""
    workflow = get_workflow()
    response = workflow.handle("show my tasks")
    await update.message.reply_text(response, parse_mode="Markdown")


async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /plan command."""
    workflow = get_workflow()
    response = workflow.handle("create a prioritized plan for today")
    await update.message.reply_text(response, parse_mode="Markdown")


async def weekly_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /weekly command."""
    await update.message.reply_text("Generating weekly summary... ⏳")
    workflow = get_workflow()
    response = workflow.handle("weekly summary report")
    await update.message.reply_text(response, parse_mode="Markdown")


async def addtask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /addtask command."""
    if not context.args:
        await update.message.reply_text("Usage: `/addtask <task title>`", parse_mode="Markdown")
        return
    title = " ".join(context.args)
    workflow = get_workflow()
    response = workflow.handle(f"add task {title}")
    await update.message.reply_text(response, parse_mode="Markdown")


async def setrepo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setrepo command."""
    if not context.args:
        await update.message.reply_text("Usage: `/setrepo owner/repo`", parse_mode="Markdown")
        return
    repo = context.args[0]
    workflow = get_workflow()
    response = workflow.handle(f"set repo {repo}")
    await update.message.reply_text(response)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all non-command text messages."""
    user_message = update.message.text
    if not user_message:
        return

    workflow = get_workflow()
    response = workflow.handle(user_message)
    await update.message.reply_text(response, parse_mode="Markdown")


def main() -> None:
    """Start the Telegram bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in .env")
        sys.exit(1)

    logger.info("Starting Hermes Dev Assistant...")

    app = (
        Application.builder()
        .token(token)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .build()
    )

    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("standup", standup_command))
    app.add_handler(CommandHandler("issues", issues_command))
    app.add_handler(CommandHandler("tasks", tasks_command))
    app.add_handler(CommandHandler("plan", plan_command))
    app.add_handler(CommandHandler("weekly", weekly_command))
    app.add_handler(CommandHandler("addtask", addtask_command))
    app.add_handler(CommandHandler("setrepo", setrepo_command))

    # Register message handler (must be last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling
    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
