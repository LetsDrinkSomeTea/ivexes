FROM kalilinux/kali-rolling
LABEL authors="julian"

RUN apt update && apt -y install kali-linux-headless

RUN apt update && apt install -y strace

RUN echo 'root:passwd' | chpasswd
RUN useradd -m -s /bin/bash user && echo 'user:passwd' | chpasswd
RUN echo 'user  ALL=(ALL:ALL) NOPASSWD: ALL' > /etc/sudoers.d/user

# Force enabling root login and password authentication
RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENTRYPOINT ["/usr/sbin/sshd", "-D"]
