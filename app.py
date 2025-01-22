from flask import Flask, render_template, request, abort
import face_recognition
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration de l'application
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limite : 2 Mo par fichier


def allowed_file(filename):
    """
    Vérifie si le fichier a une extension autorisée.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """
    Page d'accueil de l'application.
    """
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """
    Route pour traiter les fichiers téléchargés et comparer les visages.
    """
    if 'known_image' not in request.files or 'unknown_image' not in request.files:
        return "<h2>Erreur : Vous devez télécharger deux fichiers.</h2>", 400

    known_file = request.files['known_image']
    unknown_file = request.files['unknown_image']

    # Validation des fichiers
    if not (known_file and allowed_file(known_file.filename)):
        return "<h2>Erreur : Le fichier connu n'est pas valide ou son type n'est pas autorisé.</h2>", 400
    if not (unknown_file and allowed_file(unknown_file.filename)):
        return "<h2>Erreur : Le fichier inconnu n'est pas valide ou son type n'est pas autorisé.</h2>", 400

    # Sécurisation des noms de fichiers
    known_filename = secure_filename(known_file.filename)
    unknown_filename = secure_filename(unknown_file.filename)

    # Enregistrement des fichiers temporairement
    known_path = os.path.join(app.config['UPLOAD_FOLDER'], known_filename)
    unknown_path = os.path.join(app.config['UPLOAD_FOLDER'], unknown_filename)

    known_file.save(known_path)
    unknown_file.save(unknown_path)

    # Traitement des fichiers
    try:
        known_image = face_recognition.load_image_file(known_path)
        unknown_image = face_recognition.load_image_file(unknown_path)

        known_encoding = face_recognition.face_encodings(known_image)[0]
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

        results = face_recognition.compare_faces([known_encoding], unknown_encoding)
        message = "Les visages correspondent !" if results[0] else "Les visages ne correspondent pas."
    except IndexError:
        message = "Aucun visage détecté dans l'une des images. Veuillez réessayer avec d'autres images."
    except Exception as e:
        message = f"Erreur inattendue : {e}"

    # Nettoyage des fichiers téléchargés
    os.remove(known_path)
    os.remove(unknown_path)

    return f"<h2>Résultat : {message}</h2>"


if __name__ == '__main__':
    # Crée le dossier pour stocker les fichiers si nécessaire
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=False)
