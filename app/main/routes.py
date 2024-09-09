from app.main import bp

@bp.route('/')
@bp.route('/home')
def home():
    return 'npm visual home page here'
