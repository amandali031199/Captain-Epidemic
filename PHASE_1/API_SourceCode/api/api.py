import flask
from flask import request, jsonify,send_from_directory, make_response, Flask,  Blueprint
import sqlite3
from flask_swagger_ui import get_swaggerui_blueprint
from flask_restplus import Api, Resource, fields
import datetime
import re


app = Flask(__name__)
app.config.SWAGGER_UI_OAUTH_APP_NAME = 'Teletubbies Api'
api = Api(app, title=app.config.SWAGGER_UI_OAUTH_APP_NAME,description="This is API developed by the team Teletubbies using a database with information from WHO ")

class Article(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'No data found')
    @api.response(403, 'Invalid format')
    @api.doc(params={'start_date': 'Start date for the articles. Use format YYYY-MM-DDTHH:MM:SS'})
    @api.doc(params={'end_date': 'End date for the articles. Use format YYYY-MM-DDTHH:MM:SS'})
    @api.doc(params={'key_terms': 'The key terms to look for when finding article. Separate multiple key terms by comma'})
    @api.doc(params={'location': 'The country where the epidemic takes place'})
    def get(self, start_date,end_date):
        # pattern match start and end date
        # re.search("^[0-9][0-9]\-[0-9]\-[0-9]T[0-9]:[0-9]:[0-9}$", start_date)
        # if not x:
        #   # return 403 api.abort(403)
        location = request.args.get('location')
        if not location:
            location = ""
        key_terms = request.args.get('key_terms')
        if not key_terms:
            key_terms = ""
        final_start,final_end = self.convert_date_to_int(start_date,end_date)
        if final_end < final_start:
            return "End date must be larger than start date",404
        articles = self.check_data_exists(final_start,final_end,location,key_terms)
        if articles == False:
            return "No data found",404
        result = self.get_results(articles)
        return result,200

    @api.response(403, 'Not Authorized')
    def post(self, id):
        api.abort(403)

    @api.response(403, 'Not Authorized')
    def put(self, id):
        api.abort(403)

    @api.response(403, 'Not Authorized')
    def delete(self, id):
        api.abort(403)

    # check if any data exists for the query
    def check_data_exists(self,start_date,end_date,location,key_terms):
        conn = sqlite3.connect('who.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()
        query = 'SELECT r.id,a.headline,a.main_text,a.date_of_publication,a.url,r.event_date from Article a JOIN Report r on r.url = a.url where a.date_of_publication >=' + start_date + ' and a.date_of_publication <=' + end_date + ';'
        if location != '' and key_terms != '':
            query = 'SELECT * from Article a JOIN Report r on r.url = a.url JOIN Location l on l.ReportID = r.id JOIN Disease d on d.ReportID = r.id where a.date_of_publication >=' + start_date + ' and a.date_of_publication <=' + end_date + ' and l.location = \'' + location + '\'  and d.Disease = \'' + key_terms + '\';'
        elif location != '':
            query = 'SELECT r.id,a.headline,a.main_text,a.date_of_publication,a.url,l.location,r.event_date from Article a JOIN Report r on r.url = a.url JOIN Location l on l.ReportID = r.id where a.date_of_publication >=' + start_date + ' and a.date_of_publication <=' + end_date + ' and l.location = \'' + location + '\';'
        elif key_terms != '':
            if ',' in key_terms:
                k = key_terms.split(',')
                i = 1
                query = 'SELECT r.id,a.headline,a.main_text,a.date_of_publication,a.url,r.event_date,d.disease from Article a JOIN Report r on r.url = a.url JOIN Disease d on d.ReportID = r.id where a.date_of_publication >=' + start_date + ' and a.date_of_publication <=' + end_date + ' and d.Disease = \'' + k[0] + '\''
                while i < len(k):
                    query = query + ' UNION SELECT r.id,a.headline,a.main_text,a.date_of_publication,a.url,r.event_date,d.disease from Article a JOIN Report r on r.url = a.url JOIN Disease d on d.ReportID = r.id where a.date_of_publication >=' + start_date + ' and a.date_of_publication <=' + end_date + ' and d.Disease = \'' + k[i] + '\''
                    i+=1
                query = query + ';'
            else:
                query = 'SELECT r.id,a.headline,a.main_text,a.date_of_publication,a.url,r.event_date,d.disease from Article a JOIN Report r on r.url = a.url JOIN Disease d on d.ReportID = r.id where a.date_of_publication >=' + start_date + ' and a.date_of_publication <=' + end_date + ' and d.Disease = \'' + key_terms + '\';'
        results = cur.execute(query).fetchall()
        articles = {}
        if len(results) == 0:
            return False
        for r in results:
            if r['url'] in articles:
                u = r['url']
                articles[u].append(r['id'])
            else:
                arr = []
                arr.append(r['id'])
                u = r['url']
                articles[u] = arr
        return articles

    # compile the results into correct format
    def get_results(self,articles):
        conn = sqlite3.connect('who.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()
        res = []
        for key in articles:
            query = 'SELECT a.url,a.date_of_publication,a.headline,a.main_text from Article a WHERE a.url = \'' + key + '\';'
            data = cur.execute(query).fetchall()
            data[0]['reports'] = []
            # change publication date format
            date = str(data[0]['date_of_publication'])
            data[0]['date_of_publication'] = date[0:4] + '-' + date[4:6] + '-' + date[6:8] + ' ' + date[8:10] + ':' + date[10:12] + ':' + date[12:14]
            for id in articles[key]:
                query = 'SELECT * from Report r left join Syndrome s on s.ReportID = r.id left join Location l on l.ReportID = r.id left join Disease d on d.ReportID = r.id where r.id =' + str(id) + ';'
                report = cur.execute(query).fetchall()
                b = {}
                if len(report) > 0:
                    b['event_date'] = report[0]['event_date']
                # get list of locations, diseases and syndromes
                b['locations'] = []
                b['diseases'] = []
                b['syndromes'] = []
                for l in report:
                    if l['Country'] or l['Location']:
                        places = {}
                        if not l['Country']:
                            l['Country'] = ""
                        if not l['Location']:
                            l['Location']= ""
                        places['country'] = l['Country']
                        places['location'] = l['Location']
                        if places not in b['locations']:
                            b['locations'].append(places)
                    else:
                        b['locations'] = ""
                    if l['Disease'] :
                        if l['Disease'] not in b['diseases']:
                            b['diseases'].append(l['Disease'])
                    else:
                        b['diseases'] = ""
                    if l['Symptom'] :
                        if l['Symptom'] not in b['syndromes']:
                            b['syndromes'].append(l['Symptom'])
                    else:
                        b['syndromes'] = ""
                data[0]['reports'].append(b)
            res.append(data[0])
        return res

    def convert_date_to_int(self,start_date,end_date):
        start_day,start_time = start_date.split('T')
        end_day,end_time = end_date.split('T')
        sd = start_day.replace("-","")
        ed = end_day.replace("-","")
        st = start_time.replace(":","")
        et = end_time.replace(":","")
        final_start = sd + st
        final_end = ed + et
        return final_start,final_end

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static',path)


### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Teletubbies-API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

api.add_resource(Article, "/article/<string:start_date>/<string:end_date>")
app.run(debug=True)
