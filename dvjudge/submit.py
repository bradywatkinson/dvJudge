from flask import render_template, request, flash, url_for, redirect
from dvjudge import app

@app.route('/submit', methods=['POST'])
def submit_specific_problem():
    flash ("Successfully submitted for problem " + request.args.get('problem_id'))
    # TODO: No validation
    return redirect(url_for('browse'))
