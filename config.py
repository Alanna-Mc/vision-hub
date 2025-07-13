import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    # Where to save profile photos
    PROFILE_PHOTO_FOLDER = os.path.join(basedir,
                                        'app',
                                        'static',
                                        'images',
                                        'profilePhoto')

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """
        Check that the filename has one of our allowed extensions.
        """
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in Config.ALLOWED_EXTENSIONS