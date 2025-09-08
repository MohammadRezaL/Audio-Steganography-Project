from flask import Flask, render_template, request, send_file, jsonify
import wave

app = Flask(__name__)

# ===== Caesar Cipher =====
def caesar_encrypt(text, shift=3):
    result = ""
    for char in text:
        if char.isalpha():
            start = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - start + shift) % 26 + start)
        else:
            result += char
    return result

def caesar_decrypt(text, shift=3):
    return caesar_encrypt(text, -shift)

# ===== Encode =====
def encode_wav(audio_in, message, shift=3, max_chars=50):
    if len(message) > max_chars:
        return None, f"❌ Maximum {max_chars} characters allowed."

    encrypted_msg = caesar_encrypt(message, shift)

    song = wave.open(audio_in, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    encrypted_msg = encrypted_msg + '###'
    bits = ''.join([format(ord(i), '08b') for i in encrypted_msg])

    if len(bits) > len(frame_bytes):
        return None, "❌ Audio file does not have enough capacity!"

    for i in range(len(bits)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(bits[i])

    output_file = "static/output_stego.wav"
    with wave.open(output_file, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(bytes(frame_bytes))
    song.close()
    return output_file, "✅ Message hidden successfully!"

# ===== Decode =====
def decode_wav(audio_in, shift=3):
    song = wave.open(audio_in, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    string = "".join(
        chr(int("".join(map(str, extracted[i:i+8])), 2))
        for i in range(0, len(extracted), 8)
    )
    encrypted_msg = string.split("###")[0]
    decrypted_msg = caesar_decrypt(encrypted_msg, shift)
    song.close()
    return decrypted_msg

# ===== Routes =====
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/encode', methods=['POST'])
def encode_route():
    file = request.files['audio']
    message = request.form['message']
    shift = int(request.form['shift'])
    file.save("temp.wav")

    output, status = encode_wav("temp.wav", message, shift)
    if output:
        return send_file(output, as_attachment=True)
    return jsonify({"error": status})

@app.route('/decode', methods=['POST'])
def decode_route():
    file = request.files['audio']
    shift = int(request.form['shift'])
    file.save("temp.wav")
    msg = decode_wav("temp.wav", shift)
    return jsonify({"message": msg})

if __name__ == "__main__":
    app.run(debug=True)
