cd /root/work/project/WHUClubSynapse/backend/AI/AIserver/
python start_server.py
ngrok http http://localhost:8080
python train_decoder.py configs/decoder_amazon.gin