import asyncio
import sys
from pathlib import Path

from loguru import logger

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from core.bot.services import ChatGptService

    chatgpt_service = ChatGptService.build()
    asyncio.run(chatgpt_service.update_chatgpt_models())
    logger.info("chatgpt models has been updated")
