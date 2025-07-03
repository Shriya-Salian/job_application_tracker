# from flask import Flask, render_template,request

# app = Flask (__name__)
# jobs =[]

# @app.route('/',methods=['GET','POST'])  #app route decorator

# def index():
#     if request.method == 'POST':
#         url = request.form['url']
#         jobs.append(url)
#     return render_template('index.html',jobs=jobs)

# if __name__ == '__main__':
#     app.run(debug = True)


from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Local MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client['job_tracker']
jobs_collection = db['jobs']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        job_data = {
            "url": url,
            "title": "Unknown",     # Will be updated later
            "company": "Unknown",   # Will be updated later
            "status": "Not Applied"
        }
        jobs_collection.insert_one(job_data)

    all_jobs = list(jobs_collection.find())
    return render_template('index.html', jobs=all_jobs)

@app.route('/update_status/<job_id>', methods=['POST'])
def update_status(job_id):
    new_status = request.form['status']
    jobs_collection.update_one(
        {"_id": job_id},
        {"$set": {"status": new_status}}
    )
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)