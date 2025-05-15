# Dockerfile
FROM archlinux:latest
RUN pacman -Syu --noconfirm

# Basis-Tools
RUN pacman -S --noconfirm \
      neovim \
      python3 \
      python-pip \
      curl \
      git \
      zip \
      unzip \
      wget \
      ripgrep \
      gcc \
      go \
      cargo \
      luarocks \
      ruby \
      jre21-openjdk \
      nodejs \
      npm

# nvim-Config für LSP (z.B. pyright bei Python)
RUN mkdir -p /root/.config/nvim
COPY nvim-conf/ /root/.config/nvim

# Arbeitsverzeichnis (Code-Base mounten wir später als /workspace)
WORKDIR /workspace

# Neovim headless starten und auf Socket lauschen
CMD ["nvim", "--headless", "--listen", "0.0.0.0:8080"]

