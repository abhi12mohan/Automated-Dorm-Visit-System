from visit import app

app.secret_key = 'random_secret_key_you_cant_guess'
app.run(host='0.0.0.0')
