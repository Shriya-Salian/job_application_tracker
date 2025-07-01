from flask import Flask, render_template,request

app = Flask (__name__)
jobs =[]

@app.route('/',methods=['GET','POST'])  #app route decorator

def index():
    if request.method == 'POST':
        url = request.form['url']
        jobs.append(url)
    return render_template('index.html',jobs=jobs)

if __name__ == '__main__':
    app.run(debug = True)
