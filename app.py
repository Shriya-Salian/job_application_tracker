from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
import scraper  # Make sure scraper.py is in same folder

app = Flask(__name__)

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017")
db = client['job_tracker']
jobs_collection = db['jobs']


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']

        details = scraper.extract_job_details(url)

        job_data = {
            "url": url,
            "title": details['title'],
            "company": details['company'],
            "status": "Not Applied",
            "job_id": details['job_id'],
            "source": details.get('source', 'Unknown')
        }

        jobs_collection.insert_one(job_data)

    all_jobs = list(jobs_collection.find())
    return render_template('index.html', jobs=all_jobs)


@app.route('/update_status/<job_id>', methods=['POST'])
def update_status(job_id):
    new_status = request.form['status']
    try:
        object_id = ObjectId(job_id)
    except:
        return redirect(url_for('index'))

    jobs_collection.update_one(
        {"_id": object_id},
        {"$set": {"status": new_status}}
    )
    return redirect(url_for('index'))

@app.route('/delete_job/<job_id>', methods=['POST'])
def delete_job(job_id):
    try:
        object_id = ObjectId(job_id)
    except:
        return redirect(url_for('index'))

    jobs_collection.delete_one({"_id": object_id})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)