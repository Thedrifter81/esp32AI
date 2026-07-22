import os
import sys
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# Recupera la chiave OpenAI
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@app.route('/upload', methods=['POST'])
def upload_audio():
    print("--> Nuova richiesta ricevuta dall'ESP32!", flush=True)
    
    try:
        # Legge il flusso di dati in modo sicuro per evitare crash di memoria
        audio_data = request.get_data()
        print(f"--> Byte ricevuti: {len(audio_data)}", flush=True)
        
        if len(audio_data) < 100:
            print("--> Errore: File troppo piccolo o vuoto!", flush=True)
            return "File audio non valido", 400

        # Salva il file WAV temporaneo
        with open("temp.wav", "wb") as f:
            f.write(audio_data)
            
        print("--> File temp.wav salvato. Invio a Whisper...", flush=True)
        
        # 1. Trascrizione con Whisper
        with open("temp.wav", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        
        print(f"--> Trascrizione completata: {transcript.text}", flush=True)
        
        # 2. Risposta con ChatGPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Rispondi in italiano in modo brevissimo ed essenziale, massimo due frasi."},
                {"role": "user", "content": transcript.text}
            ]
        )
        reply = response.choices[0].message.content
        print(f"--> Risposta ChatGPT generata con successo!", flush=True)
        return reply, 200
        
    except Exception as e:
        # Forza la scrittura dell'errore nei log di Render, visibile anche in caso di crash
        print(f"!!! CRASH INTERNO DEL SERVER: {str(e)}", file=sys.stderr, flush=True)
        return f"Errore interno: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
