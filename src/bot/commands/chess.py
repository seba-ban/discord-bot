import argparse
import io
import shlex
from dataclasses import asdict

import chess
import chess.engine
import chess.svg
import discord
from cairosvg import svg2png
from discord.ext.commands import Context
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from bot.db import session_factory
from bot.models import ChessBoard
from bot.settings import ChessSettings

from ..bot import bot

STOCKFISH_PLAYER = "stockfish"

_CACHE = {}

extras = {"tag": "chess"}


async def get_stockfish() -> chess.engine.UciProtocol:
    key = "stockfish"
    if key in _CACHE:
        return _CACHE[key]

    settings = ChessSettings()
    transport, engine = await chess.engine.popen_uci(settings.stockfish_path)

    await engine.configure(
        {
            "Hash": settings.stockfish_hash,
            "Threads": settings.stockfish_threads,
        }
    )

    _CACHE[key] = engine
    return engine


# TODO: update - probably doesn't work properly
async def analyse_board(board: chess.Board) -> str:
    eng = await get_stockfish()
    analysis = await eng.analyse(board, chess.engine.Limit(time=0.1))
    score = analysis["score"].relative
    if score.is_mate():
        mate = score.mate()
        res = f"{'-' if mate > 0 else '+'}M{abs(mate)}"
    else:
        res = f"{'+' if score.score() > 0 else '-'}{abs(score.score()) / 100.0:.2f}"
    return res


async def stockfish_move(board: chess.Board) -> chess.Move:
    eng = await get_stockfish()
    result = await eng.play(board, chess.engine.Limit(time=0.1))
    board.push(result.move)
    return result.move


def is_next_move_stockfish(
    board: chess.Board, white: str | None = None, black: str | None = None
):
    if white == STOCKFISH_PLAYER and board.turn == chess.WHITE:
        return True
    if black == STOCKFISH_PLAYER and board.turn == chess.BLACK:
        return True
    return False


async def get_board(channel_id: int) -> tuple[chess.Board, ChessBoard | None]:
    async with session_factory() as session:
        db_board = (
            await session.execute(
                select(ChessBoard).where(ChessBoard.channel_id == channel_id)
            )
        ).scalar_one_or_none()

        board = chess.Board(
            fen=chess.STARTING_FEN if db_board is None else db_board.fen
        )

        return board, db_board


async def set_board(
    channel_id: int,
    board: chess.Board,
    white: str | None = None,
    black: str | None = None,
):
    async with session_factory() as session:
        db_board = ChessBoard(
            channel_id=channel_id, fen=board.fen(), white=white, black=black
        )
        update_dict = asdict(db_board)
        query = (
            insert(ChessBoard)
            .values(**update_dict)
            .on_conflict_do_update(
                index_elements=[
                    ChessBoard.channel_id.name,
                ],
                set_=update_dict,
            )
        )
        await session.execute(query)
        await session.commit()


def get_board_img(board: chess.Board, last_move: chess.Move | None = None):
    svg_board = chess.svg.board(board, size=350, lastmove=last_move)
    return discord.File(io.BytesIO(svg2png(bytestring=svg_board)), filename="board.png")


async def send_board(
    ctx: Context, board: chess.Board, last_move: chess.Move | None = None
):
    await ctx.channel.send(file=get_board_img(board, last_move=last_move))
    if not board.is_game_over():
        next_to_move = "white" if board.turn == chess.WHITE else "black"
        await ctx.channel.send(
            f"{next_to_move}'s turn, legal moves: "
            + ", ".join(move.uci() for move in board.legal_moves)
        )


@bot.command(description="show current board", extras=extras)
async def board(ctx: Context):
    board, _ = await get_board(ctx.channel.id)
    await send_board(ctx, board)


newgame_opts = argparse.ArgumentParser(add_help=False)
newgame_opts.add_argument(
    "-w", "--white", choices=[STOCKFISH_PLAYER], help="leave unset for players to play"
)
newgame_opts.add_argument(
    "-b", "--black", choices=[STOCKFISH_PLAYER], help="leave unset for players to play"
)
newgame_opts.add_argument(
    "-f", "--fen", default=chess.STARTING_FEN, help="fen of the board"
)
newgame_opts_help = (
    "```" + "".join(newgame_opts.format_help().splitlines(keepends=True)[2:]) + "```"
)


@bot.command(description="create a new game\n" + newgame_opts_help, extras=extras)
async def newgame(ctx: Context, *, arg: str = ""):
    try:
        opts = newgame_opts.parse_args(shlex.split(arg))
    except:
        await ctx.channel.send(newgame_opts_help)
        return

    if opts.white == opts.black == STOCKFISH_PLAYER:
        await ctx.channel.send("can't have stockfish vs stockfish... yet")
        return

    try:
        board = chess.Board(fen=opts.fen)
    except:
        await ctx.channel.send("invalid fen")
        return

    move = None
    if is_next_move_stockfish(board, white=opts.white, black=opts.black):
        move = await stockfish_move(board)

    await set_board(ctx.channel.id, board, opts.white, opts.black)
    await send_board(ctx, board, last_move=move)


@bot.command(description="get current board's fen", extras=extras)
async def fen(ctx: Context):
    board, _ = await get_board(ctx.channel.id)
    await ctx.channel.send(board.board_fen())


@bot.command(description="make a move passing a valid uci string", extras=extras)
async def move(ctx: Context, uci: str):
    try:
        board, db_board = await get_board(ctx.channel.id)
        if is_next_move_stockfish(board, white=db_board.white, black=db_board.black):
            await ctx.channel.send(f"stockfish is thinking...")
            return

        uci = uci.lower()
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            await ctx.channel.send(f"Invalid move: {move}")
        else:
            board.push(move)

            if is_next_move_stockfish(
                board, white=db_board.white, black=db_board.black
            ):
                await send_board(ctx, board, last_move=move)
                move = await stockfish_move(board)

            await set_board(
                ctx.channel.id, board, white=db_board.white, black=db_board.black
            )
            await send_board(ctx, board, last_move=move)

    except chess.InvalidMoveError:
        await ctx.channel.send(f"Invalid move: {move}")


@bot.command(description="get engine analysis of the current board", extras=extras)
async def analyse(ctx: Context):
    board, _ = await get_board(ctx.channel.id)
    analysis = await analyse_board(board)
    await ctx.send(analysis)
