# Add this route to your Flask app factory
@app.route('/')
@app.route('/maintenance')
def maintenance():
    return render_template('maintenance.html')
