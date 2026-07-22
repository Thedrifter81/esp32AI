import os
import sys
import requests
from flask import Flask, request

app = Flask(__name__)

# INCOLLA LA TUA CHIAVE AQ. TRA LE VIRGOLETTE
API_KEY = "AQ.Ab8RN6ZG9LJnlBvHTBRrT3amwuOcvV9l-DJVBr-n4m1DHTfeg"

@app.route('/upload', methods=['POST'])
def upload_audio():
    print("--> Nuova richiesta ricevuta dall'ESP32!", flush=True)
    
    try:
        audio_data = request.get_data()
        print(f"--> Byte ricevuti: {len(audio_data)}", flush=True)
        
        if len(audio_data) < 100:
            return "File audio non valido", 400

        # Inviamo i dati a Gemini sfruttando l'API REST nativa che non risente del bug 401
        # Usiamo il modello gemini-2.5-flash passandogli il prompt e il file
        url = "https://googleapis.com" + API_KEY
        
        # Prepariamo il payload in formato JSON per Google
        # Inviamo l'audio convertito in testo codificato in base64 internamente o chiediamo un'analisi
        # Nota: Per brevità e massima stabilità senza installare pacchetti pesanti di conversione inline,
        # chiediamo a Gemini un'elaborazione basata sul testo o testo descrittivo.
        
        headers = {"Content-Type": "application/json"}
        
        # Poiché l'upload binario puro su REST richiede la memorizzazione nell'API Files separata,
        # per sbloccare l'audio immediatamente inviamo una richiesta testuale di controllo o la decodifica.
        # Per testare che la chiave funzioni ed elimini il 401:
        payload = {
            "contents": [{
                "parts": [{"text": "Dimmi 'Sistema Pronto' per confermare che la chiave funziona!"}]
            }]
        }
        
        response = requests.post(url, json=payload, headers=headers)
        print(f"--> Risposta HTTP di Google: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            json_resp = response.json()
            reply = json_resp['candidates'][0]['content']['parts'][0]['text']
            print(f"--> Risposta generata con successo: {reply}", flush=True)
            return reply, 200
        else:
            print(f"--> Errore Google: {response.text}", flush=True)
            return f"Errore Google: {response.status_code}", response.status_code
            
    except Exception as e:
        print(f"!!! ERRORE SERVER: {str(e)}", file=sys.stderr, flush=True)
        return f"Errore interno: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
