"""JSON API endpoints + HTML error handlers."""
from flask import Blueprint, jsonify, render_template

from ..helpers import admin_required
from ..models import Participant

bp = Blueprint('api', __name__)


@bp.route('/api/stats')
def api_stats():
    if not admin_required():
        return jsonify({'erreur': 'Non autorisé'}), 403
    return jsonify([{
        'prenom': p.prenom, 'nom': p.nom, 'email': p.email,
        'score': p.score, 'nb_reponses': p.nb_reponses,
        'date': p.date_debut.isoformat(), 'termine': p.termine,
    } for p in Participant.query.all()])


def register_error_handlers(app):
    """Attach 404 / 500 handlers to the Flask app."""

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
