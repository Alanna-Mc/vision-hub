import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User, Role, Department, TrainingModule, Question, Option, UserModuleProgress, UserQuestionAnswer


# Add shell context to work with database entities without having to import them in the command line 
# Code created with support of Miguel Grinberg's The Flash Mega Tutorial series
@app.shell_context_processor
def make_shell_context():
    return {
        'sa': sa, 
        'so': so, 
        'db': db, 
        'User': User, 
        'Role': Role, 
        'Department': Department,
        'TrainingModule': TrainingModule,
        'Question': Question,
        'Option': Option,
        'UserModuleProgress': UserModuleProgress,
        'UserQuestionAnswer': UserQuestionAnswer,
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
