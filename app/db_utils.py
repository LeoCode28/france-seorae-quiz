"""Database migration & seeding helpers."""
import json
import os
import sqlite3

from .extensions import db
from .models import Question


def migrate_db():
    """Add any missing multilingual columns on an existing SQLite DB."""
    # Flask-SQLAlchemy stocke la DB dans instance/ ou à la racine
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    possible_paths = [
        os.path.join(project_root, 'instance', 'quiz.db'),
        os.path.join(project_root, 'quiz.db'),
    ]
    db_path = next((p for p in possible_paths if os.path.exists(p)), None)
    if not db_path:
        return
    new_cols = [
        ('question_en', 'TEXT'), ('choix_en', 'TEXT'),
        ('reponse_en', 'VARCHAR(300)'),
        ('commentaire_bon_en', 'TEXT'), ('commentaire_mauvais_en', 'TEXT'),
        ('question_ko', 'TEXT'), ('choix_ko', 'TEXT'),
        ('reponse_ko', 'VARCHAR(300)'),
        ('commentaire_bon_ko', 'TEXT'), ('commentaire_mauvais_ko', 'TEXT'),
    ]
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(question)")
        existing = {row[1] for row in cur.fetchall()}
        for col, typ in new_cols:
            if col not in existing:
                cur.execute(f"ALTER TABLE question ADD COLUMN {col} {typ}")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Migration warning: {e}")


def seed_questions():
    """Seed questions from questions.json if the table is empty."""
    if Question.query.count() > 0:
        return
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(project_root, 'questions.json')
    if not os.path.exists(json_path):
        return
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    for i, q in enumerate(data):
        db.session.add(Question(
            code=str(q['code']), rue=q['rue'],
            question=q['question'],
            choix=json.dumps(q['choix'], ensure_ascii=False),
            reponse=q['reponse'],
            commentaire_bon=q['commentaire_bon'],
            commentaire_mauvais=q['commentaire_mauvais'],
            active=True, ordre=i,
        ))
    db.session.commit()
