from flask import Flask, render_template
import time
import picamera
app = Flask(__name__)
@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route("/")
def hello():
    image = "ex1.jpg"
    camera = picamera.PiCamera()
    camera.resolution = (800, 600)
    camera.capture("static/"+image)
    time.sleep(1)
    camera.close()
    return render_template("main.html")
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)