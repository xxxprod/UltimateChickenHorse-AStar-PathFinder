python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# pip3 install torch torchvision torchaudio
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install matplotlib
pip install pandas
pip install ipykernel