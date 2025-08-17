
import subprocess
import time
import os
import wave
import requests

def test_demo_server():
    """Test the demo server."""
    server_process = subprocess.Popen(["python", "-m", "TTS.server.server"])
    try:
        # Wait for the server to start
        time.sleep(30)

        # Send a request to the server
        response = requests.get("http://localhost:5002/api/tts", params={"text": "synthesis schmynthesis"}, timeout=60)
        response.raise_for_status()

        # Save the audio file
        with open("audio.wav", "wb") as f:
            f.write(response.content)

        # Check the audio file
        with wave.open("audio.wav", "rb") as wav_file:
            assert wav_file.getnframes() > 0

    finally:
        # Kill the server and clean up
        server_process.kill()
        os.remove("audio.wav")


def test_compute_statistics():
    """Test the compute_statistics.py script."""
    basedir = os.path.dirname(__file__)
    config_path = os.path.join(basedir, "../inputs/test_glow_tts.json")
    out_path = os.path.join(basedir, "../outputs/scale_stats.npy")

    # Run the script
    subprocess.check_call(["python", "TTS/bin/compute_statistics.py", "--config_path", config_path, "--out_path", out_path])

    # Check that the output file was created
    assert os.path.exists(out_path)

    # Clean up
    os.remove(out_path)
