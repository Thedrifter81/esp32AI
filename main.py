import os
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# Recupera la chiave OpenAI in modo sicuro dalle impostazioni del server
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@app.route('/upload', methods=['POST'])
def upload_audio():
    audio_data = request.data
    
    # Salva temporaneamente i byte audio in un file
    with open("temp.wav", "wb") as f:
        f.write(audio_data)
        
    try:
        # 1. Trascrizione con Whisper
        with open("temp.wav", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        
        # 2. Risposta con ChatGPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Rispondi in italiano in modo brevissimo ed essenziale, massimo due frasi."},
                {"role": "user", "content": transcript.text}
            ]
        )
        return response.choices[0].message.content, 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Render richiede l'avvio sulla porta definita dalla variabile d'ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
