FROM python:3.11 as stockfish_builder

WORKDIR /stockfish_builder

# TODO: use args to specify version and arch
RUN git clone https://github.com/official-stockfish/Stockfish.git \
    && cd Stockfish/src \
    && git checkout sf_16 \
    && make -j profile-build ARCH=armv8 \
    && mv stockfish /usr/local/bin/stockfish

FROM python:3.11 as main

WORKDIR /app

COPY ./ ./

RUN apt-get update \
    && apt install libcairo2 libffi-dev \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install

COPY --from=stockfish_builder /usr/local/bin/stockfish /usr/local/bin/stockfish

ENV CHESS_STOCKFISH_PATH /usr/local/bin/stockfish

CMD ["start_bot"]