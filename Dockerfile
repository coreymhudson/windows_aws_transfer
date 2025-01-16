FROM mcr.microsoft.com/windows/servercore:ltsc2019

WORKDIR /app

# Install Python
RUN powershell -Command \
    Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.9.10/python-3.9.10-amd64.exe -OutFile python-installer.exe; \
    Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -NoNewWindow -Wait; \
    Remove-Item python-installer.exe

# Install PyInstaller
RUN pip install pyinstaller

# Copy application files
COPY . /app

# Build the Windows executable
RUN pyinstaller --onefile --noconsole app.py

# Specify output
CMD ["cmd"]
