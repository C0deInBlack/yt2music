FROM alpine

WORKDIR /app

ENV PATH="/app:${PATH}"

ENV INTERACTIVE=0

COPY . .

RUN apk add --no-cache python3 py3-pip bash \
    py3-eyed3 py3-requests ffmpeg git pipx python3-dev \
    imagemagick

RUN pipx install rich --include-deps

RUN wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -P /app 

RUN chmod +x yt-dlp app.py setup.py main.py

# RUN python setup.py build_ext --inplace

# RUN adduser -D -H dockeruser

# USER dockeruser

ENTRYPOINT ["python", "app.py"]

CMD []
