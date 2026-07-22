import os
import sys
import requests
from flask import Flask, request

app = Flask(__name__)

# LA TUA CHIAVE DI AUTENTICAZIONE GOOGLE
API_KEY = "AQ.Ab8RN6ZG9LJnlBvHTBRrT3amwuOcvV9l-DJVBr-n4m1DHTfeg"

@app.route('/upload', methods=['POST'])
def upload_audio():
    print("--> Richiesta ricevuta dall'ESP32!", flush=True)
    
    try:
        audio_data = request.get_data()
        print(f"--> Byte ricevuti dall'hardware: {len(audio_data)}", flush=True)
        
        # URL REST assoluto per Gemini 2.5 Flash
        url = "https://googleapis.com" + API_KEY
        
        headers = {"Content-Type": "application/json"}
        
        # Struttura dati fissa per testare l'handshake e la validità della chiave
        payload = {
            "contents": [{
                "parts": [{"text": "Rispondi in italiano dicendo esattamente: Sistema pronto e funzionante!"}]
            }]
        }
        
        # Esecuzione della richiesta HTTPS
        response = requests.post(url, json=payload, headers=headers)
        print(f"--> Codice di risposta di Google: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            json_resp = response.json()
            reply = json_resp['candidates'][0]['content']['parts'][0]['text']
            print(f"--> Testo generato dall'IA: {reply}", flush=True)
            return reply, 200
        else:
            print(f"--> Dettaglio errore da Google: {response.text}", flush=True)
            return f"Errore Google: {response.status_code}", response.status_code
            
    except Exception as e:
        print(f"!!! CRASH INTERNO DEL SERVER: {str(e)}", file=sys.stderr, flush=True)
        return f"Errore: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
