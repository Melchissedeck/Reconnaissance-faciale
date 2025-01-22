from flask import Flask, render_template, request
import face_recognition

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Récupérer les fichiers téléchargés
    known_file = request.files['known_image']
    unknown_file = request.files['unknown_image']

    # Charger les images
    known_image = face_recognition.load_image_file(known_file)
    unknown_image = face_recognition.load_image_file(unknown_file)

    # Encoder les visages
    try:
        known_encoding = face_recognition.face_encodings(known_image)[0]
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

        # Comparer les visages
        results = face_recognition.compare_faces([known_encoding], unknown_encoding)
        message = "Les visages correspondent !" if results[0] else "Les visages ne correspondent pas."
    except IndexError:
        message = "Aucun visage détecté dans l'une des images. Veuillez réessayer avec d'autres images."

    return f"<h2>Résultat : {message}</h2>"

if __name__ == '__main__':
    app.run(debug=True)