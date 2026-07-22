import os
import sys
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# Configura le API di Google Gemini recuperando la chiave dal server
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

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
        
        # Carica il file audio nei server di Google usando l'SDK ufficiale
        audio_file = genai.upload_file(path="temp.wav", mime_type="audio/wav")
        print(f"--> File caricato su Google con URI: {audio_file.uri}", flush=True)
        
        # Inizializza il modello veloce e gratuito Gemini 2.5 Flash
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Chiede a Gemini di ascoltare l'audio e rispondere direttamente
        response = model.generate_content([
            audio_file,
            "Ascolta questo file audio in italiano. Genera una risposta in italiano che sia brevissima ed essenziale, massimo due frasi."
        ])
        
        # Elimina il file dai server di Google per mantenere pulito lo spazio
        genai.delete_file(audio_file.name)
        
        reply = response.text
        print(f"--> Risposta di Gemini generata con successo!", flush=True)
        return reply, 200
        
    except Exception as e:
        print(f"!!! ERRORE SERVER: {str(e)}", file=sys.stderr, flush=True)
        return f"Errore interno: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
