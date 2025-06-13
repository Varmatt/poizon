from .orders import orders_bp

def register_routes(app):
    app.register_blueprint(orders_bp)