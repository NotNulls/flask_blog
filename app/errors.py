from flask import render_template
from app import db, app

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    #it may be a fault db session so this function is resetting the db session to a clear state
    db.session.rollback()
    return render_template('500.html'), 500
