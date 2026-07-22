import os
import sys
import requests
from flask import Flask, request

app = Flask(__name__)

# CHIAVE COPIATA DIRETTAMENTE DALLA TUA VARIABILE
API_KEY = "AQ.Ab8RN6ZG9LJnlBvHTBRrT3amwuOcvV9l-DJVBr-n4m1DHTfeg"

@app.route('/upload', methods=['POST'])
def upload_audio():
    print("--> Richiesta ricevuta dall'ESP32!", flush=True)
    
    try:
        audio_data = request.get_data()
        print(f"--> Byte ricevuti: {len(audio_data)}", flush=True)
        
        # URL fisso e blindato: non può più unirsi in modo errato
        complete_url = "https://googleapis.com"
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
    "contents": [
        {
            "parts": [
                {"text": "Rispondi in italiano con la frase esatta: Sistema Pronto."}
            ]
        }
    ]
}
        
        # Esecuzione della chiamata di rete
        response = requests.post(complete_url, json=payload, headers=headers)
        print(f"--> Risposta di Google: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            json_resp = response.json()
            reply = json_resp['candidates'][0]['content']['parts'][0]['text']
            print(f"--> Testo IA generato: {reply}", flush=True)
            return reply, 200
        else:
            print(f"--> Errore da Google: {response.text}", flush=True)
            return f"Errore Google: {response.status_code}", response.status_code
            
    except Exception as e:
        print(f"!!! CRASH GENERATO: {str(e)}", file=sys.stderr, flush=True)
        return f"Errore: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
