import io

import chess
import chess.svg
import discord
from cairosvg import svg2png
from pydantic_settings import BaseSettings, SettingsConfigDict

BOARD = chess.Board()


def get_board_img(board: chess.Board, last_move: chess.Move | None = None):
    svg_board = chess.svg.board(board, size=350, lastmove=last_move)
    return discord.File(io.BytesIO(svg2png(bytestring=svg_board)), filename="board.png")


class BotSettings(BaseSettings):
    token: str

    model_config = SettingsConfigDict(env_prefix="bot_")


settings = BotSettings()

intents = discord.Intents.none()
intents.message_content = True
intents.messages = True

client = discord.Client(
    intents=intents,
)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


async def send_board(
    message: discord.Message, board: chess.Board, last_move: chess.Move | None = None
):
    await message.channel.send(file=get_board_img(board, last_move=last_move))
    if not board.is_game_over():
        next_to_move = "white" if board.turn == chess.WHITE else "black"
        await message.channel.send(
            f"{next_to_move}'s turn, legal moves: "
            + ", ".join(move.uci() for move in board.legal_moves)
        )


@client.event
async def on_message(message: discord.Message):
    global BOARD

    if message.author == client.user:
        return

    if message.content.strip() == "!board":
        await send_board(message, BOARD)
        return

    if message.content.strip() == "!newgame":
        BOARD = chess.Board()
        await send_board(message, BOARD)
        return

    if message.content.strip() == "!fen":
        await message.channel.send(BOARD.board_fen())
        return

    if message.content.startswith("!move"):
        if BOARD.is_game_over():
            await message.channel.send("start a new game by typing !newgame")

        _, _, uci = message.content.partition(" ")
        uci = uci.strip()
        try:
            move = chess.Move.from_uci(uci)
            if move not in BOARD.legal_moves:
                await message.channel.send(f"Invalid move: {uci}")
            else:
                BOARD.push(move)
                await send_board(message, BOARD, last_move=move)

        except chess.InvalidMoveError:
            await message.channel.send(f"Invalid move: {uci}")
            return


def start_bot():
    client.run(settings.token)
