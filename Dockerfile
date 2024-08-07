FROM python:3.9-alpine

WORKDIR /app
COPY . /app
RUN apk add bash udev ttf-freefont
RUN apk --no-cache add tzdata && \
        cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
        echo "Asia/Seoul" > /etc/timezone

# 한글 폰트 처리
RUN mkdir -p /usr/share/fonts/nanumfont
RUN wget http://cdn.naver.com/naver/NanumFont/fontfiles/NanumFont_TTF_ALL.zip
RUN unzip NanumFont_TTF_ALL.zip -d /usr/share/fonts/nanumfont
RUN fc-cache -f -v

# Set the lang
ENV LANG=ko_KR.UTF-8 \
    LANGUAGE=ko_KR.UTF-8
RUN pip install -r requirements.txt

EXPOSE 18080
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]
