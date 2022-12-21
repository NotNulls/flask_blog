from app import create_app, db
from app.models import Message, Notification, User, Post


app = create_app()



@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User':User, 'Post':Post, 'Notification': Notification, 'Message': Message}


if __name__ == "__main__":
    app.run(ssl_context=('cert.pem','key.pem'))