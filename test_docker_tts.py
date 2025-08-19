import requests
import os
import tempfile

def test_docker_tts_server(text="Hallo, das ist ein Test der Thorsten-Stimme!", output_file=None):
    """
    Testet den TTS-Docker-Server auf localhost:5002
    """
    if output_file is None:
        output_file = os.path.join(tempfile.gettempdir(), "docker_tts_test.wav")
    
    try:
        # TTS-Request an den Docker-Server
        url = "http://localhost:5002/api/tts"
        
        # Verschiedene API-Endpunkte versuchen
        endpoints_to_try = [
            ("http://localhost:5002/api/tts", {"text": text}),
            ("http://localhost:5002/tts", {"text": text}),
            ("http://localhost:5002/", {"text": text})
        ]
        
        for endpoint, params in endpoints_to_try:
            print(f"Versuche Endpunkt: {endpoint}")
            try:
                response = requests.post(endpoint, json=params, timeout=30)
                if response.status_code == 200:
                    # Speichere Audio-Daten
                    with open(output_file, "wb") as f:
                        f.write(response.content)
                    print(f"Erfolg! Audio gespeichert: {output_file}")
                    return output_file
                else:
                    print(f"Status Code: {response.status_code}, Response: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Fehler bei {endpoint}: {e}")
                continue
        
        # Wenn alle Endpunkte fehlschlagen, versuche einfache Verbindung
        print("Teste einfache Verbindung zum Server...")
        response = requests.get("http://localhost:5002", timeout=10)
        print(f"Server antwortet mit Status: {response.status_code}")
        print(f"Server Response: {response.text[:200]}...")
        
    except Exception as e:
        print(f"Allgemeiner Fehler: {e}")
        return None

if __name__ == "__main__":
    print("Teste Docker TTS-Server...")
    result = test_docker_tts_server()
    if result:
        print(f"Test erfolgreich! Audio-Datei: {result}")
        # Optional: Audio-Datei abspielen
        import subprocess
        try:
            subprocess.run(["start", result], shell=True, check=False)
        except:
            print("Konnte Audio nicht automatisch abspielen.")
    else:
        print("Test fehlgeschlagen. Prüfe, ob der Docker-Container läuft:")
        print("docker ps --filter 'name=tts_thorsten_server'")
        print("docker logs tts_thorsten_server")
