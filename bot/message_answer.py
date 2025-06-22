from aiogram import html


def main_bot_command_start_message(first_name):
    message = (
            f"\U0001F590 Добро пожаловать, {html.quote(first_name)}!\n\n"
        )
    return message