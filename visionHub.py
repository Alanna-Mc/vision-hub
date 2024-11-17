import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User, Role

# Add shell context to work with database entities without having to import them in the command line
@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Role': Role}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8000", debug=True)
