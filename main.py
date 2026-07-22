import os
import sys
from flask import Flask, request
from google import genai

app = Flask(__name__)

# CONFIGURAZIONE NUOVO SDK: Incolla la tua chiave AQ. tra le virgolette
api_key = "AQ.Ab8RN6ZG9LJnlBvHTBRrT3amwuOcvV9l-DJVBr-n4m1DHTfeg"
client = genai.Client(api_key=api_key)

@app.route('/upload', methods=['POST'])
def upload_audio():
    print("--> Nuova richiesta ricevuta dall'ESP32!", flush=True)
    
    try:
        audio_data = request.get_data()
        print(f"--> Byte ricevuti: {len(audio_data)}", flush=True)
        
        if len(audio_data) < 100:
            return "File audio non valido", 400

        # Salva temporaneamente il file audio dell'ESP32 sul server
        with open("temp.wav", "wb") as f:
            f.write(audio_data)
            
        print("--> Invio del file audio direttamente a Google Gemini...", flush=True)
        
        # Carica e analizza l'audio usando il modello gratuito gemini-2.5-flash
        # Il nuovo SDK gestisce nativamente i file e l'autenticazione AQ.
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                genai.types.Part.from_bytes(
                    data=audio_data,
                    mime_type="audio/wav"
                ),
                "Ascolta questo file audio in italiano. Genera una risposta in italiano che sia brevissima ed essenziale, massimo due frasi."
            ]
        )
        
        reply = response.text
        print(f"--> Risposta di Gemini generata con successo: {reply}", flush=True)
        return reply, 200
        
    except Exception as e:
        print(f"!!! ERRORE SERVER: {str(e)}", file=sys.stderr, flush=True)
        return f"Errore interno: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
