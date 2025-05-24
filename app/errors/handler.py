from flask import Flask, render_template, url_for, flash, redirect
from app.errors import bp


@bp.app_errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html', title="Page Not Found"), 404


@bp.app_errorhandler(500)
def internal_error(error):
    return render_template('errors/504.html', title="Internal Error"), 500
