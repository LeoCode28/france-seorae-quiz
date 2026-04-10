from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, flash, abort)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict
import json, os, re
import urllib.request

load_dotenv()

app = Flask(__name__)

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════

app.secret_key = os.environ.get('SECRET_KEY', 'dev-local-only-change-in-prod')
app.config['SESSION_COOKIE_HTTPONLY']        = True
app.config['SESSION_COOKIE_SAMESITE']       = 'Lax'
app.config['SESSION_COOKIE_SECURE']         = os.environ.get('FLASK_ENV', 'development') == 'production'
app.config['SQLALCHEMY_DATABASE_URI']        = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ═══════════════════════════════════════════════════════════
#  TRADUCTIONS UI
# ═══════════════════════════════════════════════════════════

TRANSLATIONS = {
    'fr': {
        'lang_name': 'Français', 'lang_flag': '🇫🇷',
        'score_pts': 'pts',
        'back_map': '← Retour à la carte',
        'map_title': '🗺️ Le quartier Seorae',
        'map_subtitle': 'Utilise la carte pour trouver les plaques de rue. Chaque plaque a un code à 4 chiffres. Saisis-le pour répondre à la question !',
        'map_progress': 'questions répondues',
        'map_score_label': '🏆 Ton score actuel',
        'map_answered_label': '📍 Questions répondues',
        'map_enter_code': '🔢 Saisir un code',
        'map_finish': '🏁 Terminer & score',
        'map_hint': 'Les codes sont à 4 chiffres (ex : 1001). Pas besoin de compte pour jouer !',
        'gps_searching': 'Localisation en cours…',
        'gps_denied': 'Accès GPS refusé. Active-le dans ton navigateur.',
        'gps_unavailable': 'Position indisponible.',
        'gps_timeout': 'Délai dépassé. Réessaie en extérieur.',
        'gps_unsupported': 'GPS non disponible sur cet appareil',
        'gps_precision': 'Précision : ±',
        'gps_meters': ' m',
        'btn_recenter': '📍 Me localiser',
        'map_marker_code': 'Code',
        'map_marker_scan': '🔢 Utiliser ce code',
        'map_marker_hint': 'Rends-toi sur place et cherche la plaque pour trouver le code à 4 chiffres !',
        'code_title': 'Saisir un code',
        'code_subtitle': 'Tu as trouvé une plaque de rue ? Entre le code à 4 chiffres qui se trouve dessus !',
        'code_label': 'Code de la plaque',
        'code_placeholder': '1001',
        'code_validate': '✅ Valider le code',
        'code_hint': 'Les codes sont composés de 4 chiffres (ex : 1001)',
        'code_not_found': 'Code introuvable. Vérifie le numéro sur la plaque !',
        'question_already': '⚠️ Tu as déjà répondu à cette question ! Tu peux en chercher une autre sur la carte.',
        'question_point': '+1 point',
        'question_no_answer': 'Merci de choisir une réponse !',
        'question_invalid': 'Réponse invalide.',
        'result_good': 'Bonne réponse !',
        'result_bad': 'Pas tout à fait…',
        'result_score': 'Ton score',
        'result_questions': 'questions',
        'result_other_code': '🔢 Autre code',
        'result_see_map': '🗺️ Voir la carte',
        'result_finish': '🏁 Terminer & enregistrer mon score',
        'result_discover': 'En savoir plus',
        'final_stars_3': 'Magnifique ! 🏆',
        'final_stars_2': 'Très bien ! 👏',
        'final_stars_15': 'Pas mal ! 😊',
        'final_stars_1': 'Continue ! 💪',
        'final_registered': '✅ Score enregistré !',
        'final_answered': 'question(s) répondue(s)',
        'final_correct': 'bonne(s) réponse(s)',
        'final_good_pct': '% de bonnes réponses',
        'final_save_prompt': '💾 Tu veux sauvegarder ton score et apparaître dans le classement ?',
        'final_save_btn': 'Enregistrer mon score',
        'final_back_map': '🗺️ Retour à la carte',
        'final_new_player': '🔄 Nouveau joueur',
        'register_title': 'Enregistrer mon score',
        'register_subtitle': "Pour apparaître dans le classement, entre tes informations. C'est totalement facultatif !",
        'register_firstname': '👤 Prénom',
        'register_lastname': '👤 Nom',
        'register_email': '📧 Adresse e-mail',
        'register_firstname_ph': 'Ton prénom',
        'register_lastname_ph': 'Ton nom de famille',
        'register_email_ph': 'exemple@email.com',
        'register_btn': '💾 Enregistrer mon score',
        'register_skip': 'Non merci, voir mes résultats quand même →',
        'register_err_firstname': 'Le prénom est obligatoire.',
        'register_err_lastname': 'Le nom est obligatoire.',
        'register_err_email': "L'adresse e-mail est obligatoire.",
        'register_err_email_invalid': "L'adresse e-mail n'est pas valide.",
        'err_404_title': 'Page introuvable',
        'err_404_msg': "Cette page n'existe pas. Tu t'es peut-être perdu dans le quartier Seorae !",
        'err_500_title': 'Erreur serveur',
        'err_500_msg': 'Une erreur inattendue s\'est produite. Réessaie dans quelques instants !',
        'welcome_title': 'Bienvenue au Quiz France Seorae !',
        'welcome_subtitle': 'Parcours le quartier Seorae à Séoul et découvre la culture française à travers les plaques de rue du village.',
        'welcome_step1_title': 'Explore la carte',
        'welcome_step1_desc': 'Repère les plaques dans le quartier grâce à la carte interactive.',
        'welcome_step2_title': 'Trouve les plaques',
        'welcome_step2_desc': 'Rends-toi sur place et cherche la plaque de rue.',
        'welcome_step3_title': 'Entre le code',
        'welcome_step3_desc': 'Chaque plaque a un code à 4 chiffres. Saisis-le pour débloquer la question !',
        'welcome_step4_title': 'Cumule des points',
        'welcome_step4_desc': 'Réponds correctement pour gagner des points et enregistre ton score.',
        'welcome_start': '🗺️ Commencer le quiz',
        'welcome_footer': 'Un projet du Lycée Français de Séoul',
        'map_remaining': 'plaque(s) à trouver',
    },
    'en': {
        'lang_name': 'English', 'lang_flag': '🇬🇧',
        'score_pts': 'pts',
        'back_map': '← Back to map',
        'map_title': '🗺️ Seorae Village',
        'map_subtitle': 'Use the map to find the street plaques. Each plaque has a 4-digit code. Enter it to answer the question!',
        'map_progress': 'questions answered',
        'map_score_label': '🏆 Your current score',
        'map_answered_label': '📍 Questions answered',
        'map_enter_code': '🔢 Enter a code',
        'map_finish': '🏁 Finish & score',
        'map_hint': 'Codes are 4 digits (e.g. 1001). No account needed to play!',
        'gps_searching': 'Locating…',
        'gps_denied': 'GPS access denied. Enable it in your browser.',
        'gps_unavailable': 'Position unavailable.',
        'gps_timeout': 'Timeout. Try again outdoors.',
        'gps_unsupported': 'GPS not available on this device',
        'gps_precision': 'Accuracy: ±',
        'gps_meters': ' m',
        'btn_recenter': '📍 Locate me',
        'map_marker_code': 'Code',
        'map_marker_scan': '🔢 Use this code',
        'map_marker_hint': 'Go there and find the plaque to discover the 4-digit code!',
        'code_title': 'Enter a code',
        'code_subtitle': 'Found a street plaque? Enter the 4-digit code on it!',
        'code_label': 'Plaque code',
        'code_placeholder': '1001',
        'code_validate': '✅ Validate code',
        'code_hint': 'Codes are 4 digits (e.g. 1001)',
        'code_not_found': 'Code not found. Check the number on the plaque!',
        'question_already': '⚠️ You already answered this question! Find another one on the map.',
        'question_point': '+1 point',
        'question_no_answer': 'Please choose an answer!',
        'question_invalid': 'Invalid answer.',
        'result_good': 'Correct!',
        'result_bad': 'Not quite…',
        'result_score': 'Your score',
        'result_questions': 'questions',
        'result_other_code': '🔢 Another code',
        'result_see_map': '🗺️ See map',
        'result_finish': '🏁 Finish & save score',
        'result_discover': 'Learn more',
        'final_stars_3': 'Excellent! 🏆',
        'final_stars_2': 'Well done! 👏',
        'final_stars_15': 'Not bad! 😊',
        'final_stars_1': 'Keep going! 💪',
        'final_registered': '✅ Score saved!',
        'final_answered': 'question(s) answered',
        'final_correct': 'correct answer(s)',
        'final_good_pct': '% correct answers',
        'final_save_prompt': '💾 Want to save your score and appear on the leaderboard?',
        'final_save_btn': 'Save my score',
        'final_back_map': '🗺️ Back to map',
        'final_new_player': '🔄 New player',
        'register_title': 'Save my score',
        'register_subtitle': 'To appear on the leaderboard, enter your details. Totally optional!',
        'register_firstname': '👤 First name',
        'register_lastname': '👤 Last name',
        'register_email': '📧 Email address',
        'register_firstname_ph': 'Your first name',
        'register_lastname_ph': 'Your last name',
        'register_email_ph': 'example@email.com',
        'register_btn': '💾 Save my score',
        'register_skip': 'No thanks, see my results anyway →',
        'register_err_firstname': 'First name is required.',
        'register_err_lastname': 'Last name is required.',
        'register_err_email': 'Email address is required.',
        'register_err_email_invalid': 'Email address is not valid.',
        'err_404_title': 'Page not found',
        'err_404_msg': "This page doesn't exist. You may have got lost in Seorae Village!",
        'err_500_title': 'Server error',
        'err_500_msg': 'An unexpected error occurred. Please try again in a moment!',
        'welcome_title': 'Welcome to Quiz France Seorae!',
        'welcome_subtitle': 'Walk through Seorae Village in Seoul and discover French culture through the street plaques of the neighbourhood.',
        'welcome_step1_title': 'Explore the map',
        'welcome_step1_desc': 'Find the plaques in the neighbourhood using the interactive map.',
        'welcome_step2_title': 'Find the plaques',
        'welcome_step2_desc': 'Go there and look for the street plaque.',
        'welcome_step3_title': 'Enter the code',
        'welcome_step3_desc': 'Each plaque has a 4-digit code. Enter it to unlock the question!',
        'welcome_step4_title': 'Earn points',
        'welcome_step4_desc': 'Answer correctly to earn points and save your score.',
        'welcome_start': '🗺️ Start the quiz',
        'welcome_footer': 'A project by Lycée Français de Séoul',
        'map_remaining': 'plaque(s) to find',
    },
    'ko': {
        'lang_name': '한국어', 'lang_flag': '🇰🇷',
        'score_pts': '점',
        'back_map': '← 지도로 돌아가기',
        'map_title': '🗺️ 서래 마을',
        'map_subtitle': '지도를 이용해 거리 표지판을 찾아보세요. 각 표지판에는 4자리 코드가 있습니다. 코드를 입력하면 문제가 나옵니다!',
        'map_progress': '문제 답변 완료',
        'map_score_label': '🏆 현재 점수',
        'map_answered_label': '📍 답변한 문제',
        'map_enter_code': '🔢 코드 입력',
        'map_finish': '🏁 완료 & 점수 확인',
        'map_hint': '코드는 4자리 숫자입니다 (예: 1001). 계정 없이 바로 플레이하세요!',
        'gps_searching': '위치 확인 중…',
        'gps_denied': 'GPS 접근이 거부되었습니다. 브라우저에서 허용해주세요.',
        'gps_unavailable': '위치를 사용할 수 없습니다.',
        'gps_timeout': '시간 초과. 실외에서 다시 시도해주세요.',
        'gps_unsupported': '이 기기에서 GPS를 사용할 수 없습니다',
        'gps_precision': '정확도: ±',
        'gps_meters': ' m',
        'btn_recenter': '📍 내 위치',
        'map_marker_code': '코드',
        'map_marker_scan': '🔢 이 코드 사용',
        'map_marker_hint': '현장에 가서 표지판을 찾아 4자리 코드를 확인하세요!',
        'code_title': '코드 입력',
        'code_subtitle': '거리 표지판을 찾았나요? 표지판의 4자리 코드를 입력하세요!',
        'code_label': '표지판 코드',
        'code_placeholder': '1001',
        'code_validate': '✅ 코드 확인',
        'code_hint': '코드는 4자리 숫자입니다 (예: 1001)',
        'code_not_found': '코드를 찾을 수 없습니다. 표지판의 번호를 확인해주세요!',
        'question_already': '⚠️ 이미 답변한 문제입니다! 지도에서 다른 표지판을 찾아보세요.',
        'question_point': '+1 점',
        'question_no_answer': '답을 선택해주세요!',
        'question_invalid': '잘못된 답변입니다.',
        'result_good': '정답입니다!',
        'result_bad': '아쉽습니다…',
        'result_score': '현재 점수',
        'result_questions': '문제',
        'result_other_code': '🔢 다른 코드',
        'result_see_map': '🗺️ 지도 보기',
        'result_finish': '🏁 완료 & 점수 저장',
        'result_discover': '더 알아보기',
        'final_stars_3': '훌륭합니다! 🏆',
        'final_stars_2': '잘했어요! 👏',
        'final_stars_15': '나쁘지 않아요! 😊',
        'final_stars_1': '계속 도전하세요! 💪',
        'final_registered': '✅ 점수가 저장되었습니다!',
        'final_answered': '문제 답변 완료',
        'final_correct': '정답',
        'final_good_pct': '% 정답률',
        'final_save_prompt': '💾 점수를 저장하고 순위에 올라가고 싶으신가요?',
        'final_save_btn': '점수 저장',
        'final_back_map': '🗺️ 지도로 돌아가기',
        'final_new_player': '🔄 새 플레이어',
        'register_title': '점수 저장',
        'register_subtitle': '순위에 올라가려면 정보를 입력하세요. 완전히 선택 사항입니다!',
        'register_firstname': '👤 이름',
        'register_lastname': '👤 성',
        'register_email': '📧 이메일 주소',
        'register_firstname_ph': '이름을 입력하세요',
        'register_lastname_ph': '성을 입력하세요',
        'register_email_ph': 'exemple@email.com',
        'register_btn': '💾 점수 저장',
        'register_skip': '괜찮아요, 그냥 결과 보기 →',
        'register_err_firstname': '이름을 입력해주세요.',
        'register_err_lastname': '성을 입력해주세요.',
        'register_err_email': '이메일 주소를 입력해주세요.',
        'register_err_email_invalid': '유효한 이메일 주소를 입력해주세요.',
        'err_404_title': '페이지를 찾을 수 없습니다',
        'err_404_msg': '이 페이지는 존재하지 않습니다. 서래마을에서 길을 잃으셨나요!',
        'err_500_title': '서버 오류',
        'err_500_msg': '예기치 않은 오류가 발생했습니다. 잠시 후 다시 시도해주세요!',
        'welcome_title': 'Quiz France Seorae에 오신 것을 환영합니다!',
        'welcome_subtitle': '서울 서래마을을 걸으며 거리 표지판을 통해 프랑스 문화를 발견하세요.',
        'welcome_step1_title': '지도 탐색',
        'welcome_step1_desc': '인터랙티브 지도를 사용하여 동네에서 표지판을 찾으세요.',
        'welcome_step2_title': '표지판 찾기',
        'welcome_step2_desc': '현장에 가서 거리 표지판을 찾아보세요.',
        'welcome_step3_title': '코드 입력',
        'welcome_step3_desc': '각 표지판에는 4자리 코드가 있습니다. 입력하면 문제가 나옵니다!',
        'welcome_step4_title': '점수 획득',
        'welcome_step4_desc': '정답을 맞추면 점수를 얻고 기록을 저장할 수 있습니다.',
        'welcome_start': '🗺️ 퀴즈 시작',
        'welcome_footer': '서울프랑스학교 프로젝트',
        'map_remaining': '개의 표지판 남음',
    }
}

SUPPORTED_LANGS = ['fr', 'en', 'ko']

def get_lang():
    lang = session.get('lang', 'fr')
    return lang if lang in SUPPORTED_LANGS else 'fr'

def t(key):
    lang = get_lang()
    return TRANSLATIONS[lang].get(key, TRANSLATIONS['fr'].get(key, key))

@app.context_processor
def inject_globals():
    lang = get_lang()
    return dict(t=t, current_lang=lang, supported_langs=SUPPORTED_LANGS, translations=TRANSLATIONS)

# ═══════════════════════════════════════════════════════════
#  EN-TÊTES DE SÉCURITÉ HTTP
# ═══════════════════════════════════════════════════════════

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options']        = 'SAMEORIGIN'
    response.headers['X-XSS-Protection']       = '1; mode=block'
    response.headers['Referrer-Policy']        = 'strict-origin-when-cross-origin'
    return response

# ═══════════════════════════════════════════════════════════
#  MODÈLES
# ═══════════════════════════════════════════════════════════

class Question(db.Model):
    id                     = db.Column(db.Integer,     primary_key=True)
    code                   = db.Column(db.String(10),  nullable=False, unique=True)
    rue                    = db.Column(db.String(200),  nullable=False)
    # French (obligatoire)
    question               = db.Column(db.Text,         nullable=False)
    choix                  = db.Column(db.Text,         nullable=False)
    reponse                = db.Column(db.String(300),  nullable=False)
    commentaire_bon        = db.Column(db.Text,         nullable=False)
    commentaire_mauvais    = db.Column(db.Text,         nullable=False)
    # English (optionnel)
    question_en            = db.Column(db.Text,         nullable=True)
    choix_en               = db.Column(db.Text,         nullable=True)
    reponse_en             = db.Column(db.String(300),  nullable=True)
    commentaire_bon_en     = db.Column(db.Text,         nullable=True)
    commentaire_mauvais_en = db.Column(db.Text,         nullable=True)
    # Korean (optionnel)
    question_ko            = db.Column(db.Text,         nullable=True)
    choix_ko               = db.Column(db.Text,         nullable=True)
    reponse_ko             = db.Column(db.String(300),  nullable=True)
    commentaire_bon_ko     = db.Column(db.Text,         nullable=True)
    commentaire_mauvais_ko = db.Column(db.Text,         nullable=True)
    # Meta
    active                 = db.Column(db.Boolean,      default=True)
    ordre                  = db.Column(db.Integer,      default=0)

    def choix_list(self, lang='fr'):
        raw = None
        if lang == 'en' and self.choix_en:
            raw = self.choix_en
        elif lang == 'ko' and self.choix_ko:
            raw = self.choix_ko
        if not raw:
            raw = self.choix
        try:
            return json.loads(raw)
        except Exception:
            return json.loads(self.choix)

    def to_dict(self, lang='fr'):
        if lang == 'en' and self.question_en:
            question  = self.question_en
            choix     = self.choix_list('en')
            reponse   = self.reponse_en   or self.reponse
            comm_bon  = self.commentaire_bon_en   or self.commentaire_bon
            comm_mauv = self.commentaire_mauvais_en or self.commentaire_mauvais
        elif lang == 'ko' and self.question_ko:
            question  = self.question_ko
            choix     = self.choix_list('ko')
            reponse   = self.reponse_ko   or self.reponse
            comm_bon  = self.commentaire_bon_ko   or self.commentaire_bon
            comm_mauv = self.commentaire_mauvais_ko or self.commentaire_mauvais
        else:
            question  = self.question
            choix     = self.choix_list('fr')
            reponse   = self.reponse
            comm_bon  = self.commentaire_bon
            comm_mauv = self.commentaire_mauvais
        return {
            'id': self.id, 'code': self.code, 'rue': self.rue,
            'question': question, 'choix': choix, 'reponse': reponse,
            'commentaire_bon': comm_bon, 'commentaire_mauvais': comm_mauv,
            'active': self.active,
        }


class Participant(db.Model):
    id          = db.Column(db.Integer,     primary_key=True)
    prenom      = db.Column(db.String(100), nullable=False)
    nom         = db.Column(db.String(100), nullable=False)
    email       = db.Column(db.String(200), nullable=False)
    score       = db.Column(db.Integer,     default=0)
    nb_reponses = db.Column(db.Integer,     default=0)
    date_debut  = db.Column(db.DateTime,    default=datetime.utcnow)
    termine     = db.Column(db.Boolean,     default=False)


class ReponseLog(db.Model):
    __tablename__ = 'reponse_log'
    id          = db.Column(db.Integer,  primary_key=True)
    question_id = db.Column(db.Integer,  db.ForeignKey('question.id'), nullable=True)
    reponse     = db.Column(db.String(300))
    bonne       = db.Column(db.Boolean,  default=False)
    date        = db.Column(db.DateTime, default=datetime.utcnow)
    question    = db.relationship('Question', backref='logs')

# ═══════════════════════════════════════════════════════════
#  MIGRATION (colonnes multilingues sur DB existante)
# ═══════════════════════════════════════════════════════════

def migrate_db():
    import sqlite3
    # Flask-SQLAlchemy stocke la DB dans instance/ ou à la racine
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'quiz.db'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quiz.db'),
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
        cur  = conn.cursor()
        cur.execute("PRAGMA table_info(question)")
        existing = {row[1] for row in cur.fetchall()}
        for col, typ in new_cols:
            if col not in existing:
                cur.execute(f"ALTER TABLE question ADD COLUMN {col} {typ}")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Migration warning: {e}")

# ═══════════════════════════════════════════════════════════
#  SEED
# ═══════════════════════════════════════════════════════════

def seed_questions():
    if Question.query.count() > 0:
        return
    BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(BASE_DIR, 'questions.json')
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

# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

ADMIN_PASSWORD  = os.environ.get('ADMIN_PASSWORD', 'admin1234')
GOOGLE_MAPS_KEY = os.environ.get('GOOGLE_MAPS_KEY', '')
_EMAIL_RE       = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

# ═══════════════════════════════════════════════════════════
#  GOOGLE MY MAPS → PLAQUE COORDINATES (auto-sync)
#
#  Les coordonnées sont synchronisées automatiquement :
#    - Au démarrage du serveur
#    - Depuis l'admin : /admin/sync-map
#
#  Le système compare les noms des placemarks KML avec les
#  noms de rue (q.rue) dans la base de données. Aucun mapping
#  manuel n'est nécessaire : si l'admin change un code ou
#  déplace un marqueur sur Google My Maps, tout se met à jour
#  automatiquement.
# ═══════════════════════════════════════════════════════════

GOOGLE_MYMAPS_ID = os.environ.get(
    'GOOGLE_MYMAPS_ID', '18iuL7lKBF0vyFaFOhFdCTRYtpMg'
)

# Media (images + vidéos YouTube) extraits du KML, indexés par code
PLAQUE_MEDIA = {}

# Coordonnées des plaques — fallback en dur au cas où le KML est inaccessible.
# sync_plaque_coords() les met à jour automatiquement au démarrage.
PLAQUE_COORDS = {
    '1876': {'lat': 37.4959051, 'lng': 126.9980559},
    '1002': {'lat': 37.4957373, 'lng': 126.9980425},
    '5730': {'lat': 37.4955904, 'lng': 126.9980103},
    '1004': {'lat': 37.4954457, 'lng': 126.9980934},
    '2734': {'lat': 37.4950526, 'lng': 126.9980049},
    '4782': {'lat': 37.4950303, 'lng': 126.9978051},
    '6187': {'lat': 37.4940008, 'lng': 127.0010921},
    '1008': {'lat': 37.4933793, 'lng': 127.001988},
    '6976': {'lat': 37.4933176, 'lng': 127.0021006},
    '9168': {'lat': 37.4959756, 'lng': 127.0014677},
    '1011': {'lat': 37.4960437, 'lng': 127.0014032},
    '1012': {'lat': 37.4973652, 'lng': 127.0004779},
    '1493': {'lat': 37.4973923, 'lng': 127.0004759},
    '1014': {'lat': 37.4975163, 'lng': 127.0004779},
    '4594': {'lat': 37.4969333, 'lng': 126.9987505},
    '4391': {'lat': 37.496665,  'lng': 126.9975526},
    '8941': {'lat': 37.4986442, 'lng': 126.9989276},
    '1018': {'lat': 37.4989846, 'lng': 126.9988336},
    '1019': {'lat': 37.4993368, 'lng': 126.9990014},
    '3841': {'lat': 37.4998954, 'lng': 126.9981176},
    '5382': {'lat': 37.4991985, 'lng': 126.9982879},
    '1022': {'lat': 37.4988782, 'lng': 126.9984542},
    '3619': {'lat': 37.4987208, 'lng': 126.997683},
    '1024': {'lat': 37.4983334, 'lng': 126.9976401},
    '7364': {'lat': 37.4960192, 'lng': 126.9997229},
    '5942': {'lat': 37.4974036, 'lng': 126.9983349},
    '8397': {'lat': 37.4969694, 'lng': 126.9981685},
    '7194': {'lat': 37.4982314, 'lng': 126.9982919},
    '9462': {'lat': 37.4960054, 'lng': 126.9980934},
    '3942': {'lat': 37.4957117, 'lng': 126.9974953},
}


def _normalize(text):
    """Normalise un texte pour la comparaison."""
    text = text.lower().strip()
    for a, b in [('é','e'),('è','e'),('ê','e'),('ë','e'),
                 ('à','a'),('â','a'),('î','i'),('ï','i'),
                 ('ô','o'),('ù','u'),('û','u'),('ü','u'),
                 ('ç','c'),('œ','oe')]:
        text = text.replace(a, b)
    text = re.sub(r'[^\w\s]', ' ', text)
    for mot in ['rue','avenue','boulevard','place','allee','impasse','passage']:
        text = re.sub(r'\b' + mot + r'\b', '', text)
    return ' '.join(text.split())


def _match_kml_name_to_question(kml_name, questions):
    """Trouve la question qui correspond le mieux au nom KML."""
    kml_norm = _normalize(kml_name)
    kml_words = set(kml_norm.split())

    best_match = None
    best_score = 0

    for q in questions:
        rue_norm = _normalize(q.rue)
        rue_words = set(rue_norm.split())
        common = {w for w in kml_words & rue_words if len(w) > 2}
        score = len(common)
        if kml_norm in rue_norm or rue_norm in kml_norm:
            score += 3
        if score > best_score:
            best_score = score
            best_match = q.code

    return best_match if best_score >= 1 else None


def sync_plaque_coords():
    """Télécharge le KML depuis Google My Maps et met à jour PLAQUE_COORDS
    en matchant automatiquement les noms KML avec les questions en base."""
    global PLAQUE_COORDS, PLAQUE_MEDIA

    kml_url = (
        f'https://www.google.com/maps/d/kml'
        f'?mid={GOOGLE_MYMAPS_ID}&forcekml=1'
    )

    try:
        req = urllib.request.Request(kml_url, headers={
            'User-Agent': 'FranceSeorae-Quiz/1.0'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            kml_data = resp.read().decode('utf-8')
    except Exception as e:
        msg = f'Téléchargement KML échoué : {e}'
        print(f'[sync] {msg}')
        return 0, msg

    placemarks = []
    for block in kml_data.split('<Placemark>')[1:]:
        block = block.split('</Placemark>')[0]
        name_match = re.search(
            r'<name>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</name>',
            block, re.DOTALL
        )
        coords_match = re.search(
            r'<coordinates>\s*([\d\.\-]+),([\d\.\-]+)',
            block
        )
        if name_match and coords_match:
            # Extract media links (images + YouTube videos)
            images = []
            videos = []
            media_match = re.search(
                r'gx_media_links.*?<value><!\[CDATA\[(.*?)\]\]></value>',
                block, re.DOTALL
            )
            if media_match:
                for link in media_match.group(1).strip().split(' '):
                    link = link.strip()
                    if not link:
                        continue
                    if 'youtube.com/embed/' in link:
                        vid_id = link.split('youtube.com/embed/')[-1].split('?')[0]
                        videos.append(vid_id)
                    elif link.startswith('http') and 'youtube' not in link:
                        images.append(link)

            placemarks.append({
                'name': name_match.group(1).strip(),
                'lat': float(coords_match.group(2)),
                'lng': float(coords_match.group(1)),
                'images': images[:3],
                'videos': videos[:2],
            })

    if not placemarks:
        msg = 'KML téléchargé mais aucun placemark trouvé.'
        print(f'[sync] {msg}')
        return 0, msg

    try:
        with app.app_context():
            questions = Question.query.all()
    except Exception:
        questions = []

    if not questions:
        msg = 'Aucune question en base pour le matching.'
        print(f'[sync] {msg}')
        return 0, msg

    new_coords = {}
    unmatched = []

    new_media = {}
    for pm in placemarks:
        code = _match_kml_name_to_question(pm['name'], questions)
        if code:
            new_coords[code] = {'lat': pm['lat'], 'lng': pm['lng']}
            if pm['images'] or pm['videos']:
                new_media[code] = {
                    'images': pm['images'],
                    'videos': pm['videos'],
                }
        else:
            unmatched.append(pm['name'])

    if new_coords:
        PLAQUE_COORDS.update(new_coords)
    if new_media:
        PLAQUE_MEDIA.update(new_media)

    if unmatched:
        print(f'[sync] ⚠️  Non matchés : {", ".join(unmatched)}')

    msg = f'{len(new_coords)} coordonnées synchronisées depuis Google My Maps.'
    if unmatched:
        msg += f' ({len(unmatched)} placemarks non matchés)'
    print(f'[sync] ✅ {msg}')
    return len(new_coords), msg


def email_valid(e):
    return bool(_EMAIL_RE.match(e))

def init_session():
    if 'reponses_ids' not in session:
        session['reponses_ids'] = []
        session['score']        = 0

def admin_required():
    return session.get('admin_ok', False)

# ═══════════════════════════════════════════════════════════
#  ROUTE LANGUE
# ═══════════════════════════════════════════════════════════

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in SUPPORTED_LANGS:
        session['lang'] = lang
    next_url = request.args.get('next') or request.referrer or url_for('carte')
    return redirect(next_url)

# ═══════════════════════════════════════════════════════════
#  ROUTES JOUEURS
# ═══════════════════════════════════════════════════════════

@app.route('/')
def index():
    admin_ok = session.get('admin_ok', False)
    lang     = session.get('lang', 'fr')
    session.clear()
    if admin_ok:
        session['admin_ok'] = True
    session['lang']         = lang
    session['reponses_ids'] = []
    session['score']        = 0
    return render_template('accueil.html')


@app.route('/carte')
def carte():
    init_session()
    total = Question.query.filter_by(active=True).count()
    # Build map data: street name + approximate coordinates ONLY
    # NEVER send codes to the browser — users must find the physical plaques
    questions_map_data = []
    for q in Question.query.filter_by(active=True).order_by(Question.ordre, Question.id).all():
        coords = PLAQUE_COORDS.get(q.code)
        if coords:
            questions_map_data.append({
                'rue': q.rue,
                'lat': coords['lat'],
                'lng': coords['lng'],
            })
    return render_template('carte.html',
                           score=session['score'],
                           nb_repondu=len(session['reponses_ids']),
                           total=total,
                           questions_map_data=questions_map_data,
                           google_maps_key=GOOGLE_MAPS_KEY)


@app.route('/question', methods=['GET', 'POST'])
def question():
    init_session()
    lang = get_lang()

    if request.method == 'POST':
        raw = request.form.get('code', '').strip()
        raw = re.sub(r'\D', '', raw)
        try:
            code = str(int(raw)) if raw else ''
        except ValueError:
            code = ''
        q = Question.query.filter_by(code=code, active=True).first()
        if not q:
            return render_template('saisie_code.html',
                                   erreur=t('code_not_found'),
                                   score=session['score'],
                                   code_prefill='')
        deja_repondu = q.id in session['reponses_ids']
        return render_template('question.html',
                               q=q.to_dict(lang),
                               deja_repondu=deja_repondu,
                               score=session['score'])

    code_prefill = request.args.get('code', '')
    # If code provided via GET (from map marker), load question directly
    if code_prefill:
        raw = re.sub(r'\D', '', code_prefill)
        try:
            code = str(int(raw)) if raw else ''
        except ValueError:
            code = ''
        q = Question.query.filter_by(code=code, active=True).first()
        if q:
            deja_repondu = q.id in session['reponses_ids']
            return render_template('question.html',
                                   q=q.to_dict(lang),
                                   deja_repondu=deja_repondu,
                                   score=session['score'])

    return render_template('saisie_code.html', score=session['score'], code_prefill=code_prefill)


@app.route('/repondre', methods=['POST'])
def repondre():
    init_session()
    lang  = get_lang()
    total = Question.query.filter_by(active=True).count()

    try:
        question_id = int(request.form.get('question_id', ''))
    except (ValueError, TypeError):
        return redirect(url_for('carte'))

    reponse_donnee = request.form.get('reponse', '').strip()
    q_obj = db.session.get(Question, question_id)
    if not q_obj or not q_obj.active:
        return redirect(url_for('carte'))

    q = q_obj.to_dict(lang)

    if not reponse_donnee:
        return render_template('question.html',
                               q=q, deja_repondu=False,
                               score=session['score'],
                               erreur=t('question_no_answer'))

    if reponse_donnee not in q['choix']:
        return render_template('question.html',
                               q=q, deja_repondu=False,
                               score=session['score'],
                               erreur=t('question_invalid'))

    bonne        = (reponse_donnee == q['reponse'])
    reponses_ids = list(session['reponses_ids'])

    log = ReponseLog(question_id=question_id, reponse=reponse_donnee, bonne=bonne)
    db.session.add(log)
    db.session.commit()

    if question_id not in reponses_ids:
        reponses_ids.append(question_id)
        session['reponses_ids'] = reponses_ids
        session.modified        = True
        if bonne:
            session['score'] += 1

    commentaire = q['commentaire_bon'] if bonne else q['commentaire_mauvais']
    # Get media (images + videos) from KML sync
    media = PLAQUE_MEDIA.get(q_obj.code, {})
    return render_template('resultat_question.html',
                           bonne=bonne, commentaire=commentaire, q=q,
                           score=session['score'],
                           nb_repondu=len(session['reponses_ids']),
                           total=total,
                           media_images=media.get('images', []),
                           media_videos=media.get('videos', []))


@app.route('/enregistrer', methods=['GET', 'POST'])
def enregistrer():
    init_session()
    total = Question.query.filter_by(active=True).count()

    if 'participant_id' in session:
        return redirect(url_for('resultats_finaux'))

    if request.method == 'POST':
        prenom = request.form.get('prenom', '').strip()[:100]
        nom    = request.form.get('nom',    '').strip()[:100]
        email  = request.form.get('email',  '').strip()[:200].lower()

        erreurs = []
        if not prenom: erreurs.append(t('register_err_firstname'))
        if not nom:    erreurs.append(t('register_err_lastname'))
        if not email:  erreurs.append(t('register_err_email'))
        elif not email_valid(email): erreurs.append(t('register_err_email_invalid'))

        if erreurs:
            return render_template('enregistrer.html',
                                   erreur=' '.join(erreurs),
                                   score=session['score'],
                                   nb_repondu=len(session['reponses_ids']),
                                   total=total)

        p = Participant(prenom=prenom, nom=nom, email=email,
                        score=session['score'],
                        nb_reponses=len(session['reponses_ids']),
                        termine=True)
        db.session.add(p)
        db.session.commit()
        session['participant_id'] = p.id
        return redirect(url_for('resultats_finaux'))

    return render_template('enregistrer.html',
                           score=session['score'],
                           nb_repondu=len(session['reponses_ids']),
                           total=total)


@app.route('/resultats_finaux')
def resultats_finaux():
    init_session()
    total = Question.query.filter_by(active=True).count()
    p = None
    if 'participant_id' in session:
        p = db.session.get(Participant, session['participant_id'])
    return render_template('resultats_finaux.html',
                           participant=p,
                           score=session['score'],
                           nb_repondu=len(session['reponses_ids']),
                           total=total)

# ═══════════════════════════════════════════════════════════
#  ROUTES ADMIN
# ═══════════════════════════════════════════════════════════

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password', '') == ADMIN_PASSWORD:
            session['admin_ok'] = True
        else:
            return render_template('admin_login.html', erreur='Mot de passe incorrect.')
    if not admin_required():
        return render_template('admin_login.html')

    participants = Participant.query.order_by(Participant.score.desc()).all()
    total        = Question.query.filter_by(active=True).count()
    total_logs   = ReponseLog.query.count()
    correct_logs = ReponseLog.query.filter_by(bonne=True).count()
    pct_correct  = int(correct_logs / total_logs * 100) if total_logs > 0 else 0
    avg_score    = round(sum(p.score for p in participants) / len(participants), 1) if participants else 0
    termines     = sum(1 for p in participants if p.termine)

    return render_template('admin.html',
                           participants=participants, total=total,
                           total_logs=total_logs, pct_correct=pct_correct,
                           avg_score=avg_score, termines=termines)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_ok', None)
    return redirect(url_for('admin'))


@app.route('/admin/sync-map')
def admin_sync_map():
    """Synchronise les coordonnées des plaques depuis Google My Maps."""
    if not admin_required():
        return redirect(url_for('admin'))
    nb, msg = sync_plaque_coords()
    flash(f'🗺️ {msg}', 'succes')
    return redirect(url_for('admin'))


@app.route('/admin/questions')
def admin_questions():
    if not admin_required():
        return redirect(url_for('admin'))
    questions = Question.query.order_by(Question.ordre, Question.id).all()
    return render_template('admin_questions.html', questions=questions)


def _parse_question_form(form):
    """Parse and validate multilingual question form fields."""
    code = form.get('code', '').strip()
    rue  = form.get('rue',  '').strip()
    # FR
    q_fr = form.get('question', '').strip()
    c1, c2, c3 = form.get('choix1','').strip(), form.get('choix2','').strip(), form.get('choix3','').strip()
    rep_fr = form.get('reponse', '').strip()
    cb_fr  = form.get('commentaire_bon', '').strip()
    cm_fr  = form.get('commentaire_mauvais', '').strip()
    # EN
    q_en   = form.get('question_en', '').strip()
    c1e, c2e, c3e = form.get('choix1_en','').strip(), form.get('choix2_en','').strip(), form.get('choix3_en','').strip()
    rep_en = form.get('reponse_en', '').strip()
    cb_en  = form.get('commentaire_bon_en', '').strip()
    cm_en  = form.get('commentaire_mauvais_en', '').strip()
    # KO
    q_ko   = form.get('question_ko', '').strip()
    c1k, c2k, c3k = form.get('choix1_ko','').strip(), form.get('choix2_ko','').strip(), form.get('choix3_ko','').strip()
    rep_ko = form.get('reponse_ko', '').strip()
    cb_ko  = form.get('commentaire_bon_ko', '').strip()
    cm_ko  = form.get('commentaire_mauvais_ko', '').strip()

    erreurs = []
    if not code:
        erreurs.append('Le code est obligatoire.')
    elif not re.fullmatch(r'\d{1,10}', code):
        erreurs.append('Le code doit être numérique.')
    if not rue:   erreurs.append('Le nom de rue est obligatoire.')
    if not q_fr:  erreurs.append('La question (FR) est obligatoire.')
    if not (c1 and c2 and c3): erreurs.append('Les 3 choix (FR) sont obligatoires.')
    if not rep_fr: erreurs.append('La bonne réponse (FR) est obligatoire.')
    elif rep_fr not in [c1, c2, c3]: erreurs.append('La bonne réponse (FR) doit être un des 3 choix.')
    # Validate EN if partially filled
    if any([q_en, c1e, c2e, c3e, rep_en]):
        if not (c1e and c2e and c3e):
            erreurs.append('Les 3 choix (EN) sont obligatoires si la version anglaise est renseignée.')
        elif rep_en and rep_en not in [c1e, c2e, c3e]:
            erreurs.append('La bonne réponse (EN) doit être un des 3 choix anglais.')
    # Validate KO if partially filled
    if any([q_ko, c1k, c2k, c3k, rep_ko]):
        if not (c1k and c2k and c3k):
            erreurs.append('Les 3 choix (KO) sont obligatoires si la version coréenne est renseignée.')
        elif rep_ko and rep_ko not in [c1k, c2k, c3k]:
            erreurs.append('La bonne réponse (KO) doit être un des 3 choix coréens.')

    data = {
        'code': code, 'rue': rue,
        'question': q_fr,
        'choix': json.dumps([c1, c2, c3], ensure_ascii=False),
        'reponse': rep_fr,
        'commentaire_bon': cb_fr,
        'commentaire_mauvais': cm_fr,
        'question_en': q_en or None,
        'choix_en': json.dumps([c1e, c2e, c3e], ensure_ascii=False) if (c1e and c2e and c3e) else None,
        'reponse_en': rep_en or None,
        'commentaire_bon_en': cb_en or None,
        'commentaire_mauvais_en': cm_en or None,
        'question_ko': q_ko or None,
        'choix_ko': json.dumps([c1k, c2k, c3k], ensure_ascii=False) if (c1k and c2k and c3k) else None,
        'reponse_ko': rep_ko or None,
        'commentaire_bon_ko': cb_ko or None,
        'commentaire_mauvais_ko': cm_ko or None,
    }
    return erreurs, data


@app.route('/admin/questions/nouvelle', methods=['GET', 'POST'])
def admin_question_nouvelle():
    if not admin_required():
        return redirect(url_for('admin'))
    if request.method == 'POST':
        erreurs, data = _parse_question_form(request.form)
        if not erreurs and Question.query.filter_by(code=data['code']).first():
            erreurs.append(f"Le code {data['code']} est déjà utilisé.")
        if erreurs:
            return render_template('admin_question_form.html',
                                   mode='nouvelle', erreurs=erreurs,
                                   form=request.form, q=None)
        max_ordre = db.session.query(db.func.max(Question.ordre)).scalar() or 0
        q = Question(ordre=max_ordre + 1, active=True, **data)
        db.session.add(q)
        db.session.commit()
        flash(f'Question "{data["rue"]}" ajoutée avec succès !', 'succes')
        return redirect(url_for('admin_questions'))
    return render_template('admin_question_form.html',
                           mode='nouvelle', erreurs=[], form={}, q=None)


@app.route('/admin/questions/<int:qid>/modifier', methods=['GET', 'POST'])
def admin_question_modifier(qid):
    if not admin_required():
        return redirect(url_for('admin'))
    q = db.session.get(Question, qid)
    if not q:
        abort(404)
    if request.method == 'POST':
        erreurs, data = _parse_question_form(request.form)
        existing = Question.query.filter_by(code=data['code']).first()
        if existing and existing.id != qid:
            erreurs.append('Ce code est déjà utilisé par une autre question.')
        if erreurs:
            return render_template('admin_question_form.html',
                                   mode='modifier', erreurs=erreurs,
                                   form=request.form, q=q)
        for key, val in data.items():
            setattr(q, key, val)
        db.session.commit()
        flash(f'Question "{q.rue}" modifiée avec succès !', 'succes')
        return redirect(url_for('admin_questions'))

    cl_fr = q.choix_list('fr')
    cl_en = q.choix_list('en') if q.choix_en else ['', '', '']
    cl_ko = q.choix_list('ko') if q.choix_ko else ['', '', '']
    def safe(lst, i): return lst[i] if len(lst) > i else ''
    form = {
        'code': q.code, 'rue': q.rue,
        'question': q.question,
        'choix1': safe(cl_fr, 0), 'choix2': safe(cl_fr, 1), 'choix3': safe(cl_fr, 2),
        'reponse': q.reponse,
        'commentaire_bon': q.commentaire_bon, 'commentaire_mauvais': q.commentaire_mauvais,
        'question_en': q.question_en or '',
        'choix1_en': safe(cl_en, 0), 'choix2_en': safe(cl_en, 1), 'choix3_en': safe(cl_en, 2),
        'reponse_en': q.reponse_en or '',
        'commentaire_bon_en': q.commentaire_bon_en or '',
        'commentaire_mauvais_en': q.commentaire_mauvais_en or '',
        'question_ko': q.question_ko or '',
        'choix1_ko': safe(cl_ko, 0), 'choix2_ko': safe(cl_ko, 1), 'choix3_ko': safe(cl_ko, 2),
        'reponse_ko': q.reponse_ko or '',
        'commentaire_bon_ko': q.commentaire_bon_ko or '',
        'commentaire_mauvais_ko': q.commentaire_mauvais_ko or '',
    }
    return render_template('admin_question_form.html',
                           mode='modifier', erreurs=[], form=form, q=q)


@app.route('/admin/questions/<int:qid>/pause', methods=['POST'])
def admin_question_pause(qid):
    if not admin_required():
        return redirect(url_for('admin'))
    q = db.session.get(Question, qid)
    if not q:
        abort(404)
    q.active = not q.active
    db.session.commit()
    etat = 'activée' if q.active else 'mise en pause'
    flash(f'Question "{q.rue}" {etat}.', 'succes')
    return redirect(url_for('admin_questions'))


@app.route('/admin/questions/<int:qid>/supprimer', methods=['POST'])
def admin_question_supprimer(qid):
    if not admin_required():
        return redirect(url_for('admin'))
    q = db.session.get(Question, qid)
    if not q:
        abort(404)
    nom = q.rue
    ReponseLog.query.filter_by(question_id=qid).delete()
    db.session.delete(q)
    db.session.commit()
    flash(f'Question "{nom}" supprimée définitivement.', 'succes')
    return redirect(url_for('admin_questions'))


@app.route('/admin/logs')
def admin_logs():
    if not admin_required():
        return redirect(url_for('admin'))
    questions = Question.query.order_by(Question.ordre, Question.id).all()
    q_stats   = []
    for q in questions:
        logs           = ReponseLog.query.filter_by(question_id=q.id).all()
        total_attempts = len(logs)
        correct        = sum(1 for l in logs if l.bonne)
        pct            = int(correct / total_attempts * 100) if total_attempts > 0 else None
        q_stats.append({'id': q.id, 'rue': q.rue, 'code': q.code, 'active': q.active,
                        'attempts': total_attempts, 'correct': correct, 'pct': pct})

    q_stats_hardest = sorted([s for s in q_stats if s['pct'] is not None], key=lambda x: x['pct'])[:10]
    q_stats_popular = sorted(q_stats, key=lambda x: x['attempts'], reverse=True)[:10]

    participants = Participant.query.all()
    total_logs   = ReponseLog.query.count()
    correct_logs = ReponseLog.query.filter_by(bonne=True).count()
    pct_global   = int(correct_logs / total_logs * 100) if total_logs > 0 else 0
    avg_score    = round(sum(p.score for p in participants) / len(participants), 1) if participants else 0
    termines     = sum(1 for p in participants if p.termine)
    recent       = ReponseLog.query.order_by(ReponseLog.date.desc()).limit(30).all()

    daily = defaultdict(int)
    for p in participants:
        daily[p.date_debut.strftime('%d/%m')] += 1
    daily_sorted = list(daily.items())[-14:]
    max_daily    = max((v for _, v in daily_sorted), default=1)

    score_dist = defaultdict(int)
    for p in participants:
        score_dist[(p.score // 5) * 5] += 1

    return render_template('admin_logs.html',
                           q_stats=q_stats,
                           q_stats_hardest=q_stats_hardest,
                           q_stats_popular=q_stats_popular,
                           total_logs=total_logs, correct_logs=correct_logs,
                           pct_global=pct_global, avg_score=avg_score,
                           termines=termines, total_participants=len(participants),
                           recent=recent, daily_sorted=daily_sorted,
                           max_daily=max_daily, score_dist=dict(score_dist))

# ═══════════════════════════════════════════════════════════
#  API & ERREURS
# ═══════════════════════════════════════════════════════════

@app.route('/api/stats')
def api_stats():
    if not admin_required():
        return jsonify({'erreur': 'Non autorisé'}), 403
    return jsonify([{
        'prenom': p.prenom, 'nom': p.nom, 'email': p.email,
        'score': p.score, 'nb_reponses': p.nb_reponses,
        'date': p.date_debut.isoformat(), 'termine': p.termine,
    } for p in Participant.query.all()])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# ═══════════════════════════════════════════════════════════
#  INITIALISATION (fonctionne en local ET sur PythonAnywhere)
# ═══════════════════════════════════════════════════════════

with app.app_context():
    db.create_all()
    migrate_db()
    seed_questions()

# Synchronise les coordonnées depuis Google My Maps
print('[startup] Synchronisation des coordonnées depuis Google My Maps...')
sync_plaque_coords()

# ═══════════════════════════════════════════════════════════
#  DÉMARRAGE LOCAL (ignoré par PythonAnywhere / WSGI)
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true',
            host='127.0.0.1')
