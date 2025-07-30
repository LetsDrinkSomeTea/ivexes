FROM kalilinux/kali-rolling:latest
LABEL authors="julian"

RUN apt-get update && apt-get -y install kali-linux-headless

RUN useradd -m user && echo "user:passwd" | chpasswd && echo "root:passwd" | chpasswd

