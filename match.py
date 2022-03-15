"""
Created on Mon Feb 21 10:57:41 2022

@author: kenth
"""
from riotwatcher import LolWatcher, ApiError
from IPython.display import display
from flask import Flask, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import pandas as pd
import os

PROFILEICON_FOLDER = os.path.join('static', 'img', 'profileicon')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///league.db'
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = PROFILEICON_FOLDER

"""
class Summoner(db.Model):
    name = db.Column(db.String, primary_key=True)
    profileIconId = db.Column(db.Integer, primary_key=True)
    
    def __repr__(self):
        return '<Summoner %r>' % self.id
"""
#----dropdown for regions
#@app.route('/', methods = ['GET'])
#def dropdown():
#    regions = ['NA1', 'EUW1', 'EUN1', 'BR1', 'LA1', 'LA2', 'OCE', 'RU1', 'TR1', 'JP1', 'KR'] #region codes
#    return render_template('index.html', regions = regions) #regions is the dropdown menu variable name
#----

@app.route('/', methods=['POST', 'GET']) #main page that will be loaded first.
def Main():
    if request.method == 'POST':
        sumname = request.form['content'] #gets summoner name from inputed text.
        #profile = Summoner(name=sumname)
        region = 'NA1' #for now we will focus on the North American server.
        
        try:
            summonerdict = watcher.summoner.by_name(region, sumname) #pulls summoner data from riot api into a dictionary
            subsets_needed = ['name', 'profileIconId', 'summonerLevel'] #for now all we need is name, profileIconId, and summonerLevel.
            demodict = {key: summonerdict[key] for key in subsets_needed} #separates the keys we need form the dictionary
            nameid = demodict['name']
            imgid = demodict['profileIconId']
            Levelid = demodict['summonerLevel']
            name = str(nameid)
            sumonnerLevel = str(Levelid)
            profile_icon_id = str(imgid) +'.png'
            profileicon_file_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_icon_id)
            #return demodict
            return render_template('index.html', profile_img = profileicon_file_path) #pass profile_img as variable for
            #note: change index.html(search page) to summoner.html(result page)
        except:
            return "there was an issue searching for this summoner or this summoner does not exist."  #incase the summoner name being searched for does not exist.
    else:
        return render_template('index.html') 

@app.route('/summoner/<string:name>', methods=['GET', 'POST'])
def summoner(name):
    
    #user1 = request.form.get['Username']
    #region1 = request.form.get['region']
    """
    summonerdf = watcher.summoner.by_name(region, name)
    summonerdf['profileIconId']
    summonerdf['summonerLevel']
    """
    return "hello"


# global variables
api_key = 'RGAPI-a8d687c5-a009-4008-97bd-82ca0305cee3'
watcher = LolWatcher(api_key)
#region = input("Enter your region: ")
#name = input("Enter your Summoner Name(Case Sensitive): ")
#region = region.upper()
#match_region = 'NA'

"""
if region == 'NA':
    region = 'NA1';
elif region == 'BR':
    region = 'BR1';
elif region == 'LAN':
    region = 'LA1';
elif region == 'LAS':
    region = 'LA2';
elif region == 'OCE':
    region = 'OC1';
elif region == 'KR':
    region = 'KR';
elif region == 'JP':
    region = 'JP1';
elif region == 'EUNE':
    region = 'EUN1';
elif region == 'EUW':
    region = 'EUW1';
elif region == 'RU':
    region = 'RU';
elif region == 'TR':
    region = 'TR1';

if region == 'NA1':
    match_region = 'AMERICAS';
elif region == 'BR1':
    match_region = 'AMERICAS';
elif region == 'LA1':
    match_region = 'AMERICAS';
elif region == 'LA2':
    match_region = 'AMERICAS';
elif region == 'OC1':
    match_region = 'AMERICAS';
elif region == 'KR':
    match_region = 'ASIA';
elif region == 'JP1':
    match_region = 'ASIA';
elif region == 'EUN1':
    match_region = 'EUROPE';
elif region == 'EUW1':
    match_region = 'EUROPE';
elif region == 'RU':
    match_region = 'EUROPE';
else:
    match_region = 'EUROPE';


me = watcher.summoner.by_name(region, name)

print(me['summonerLevel'])
print(me['profileIconId'])


my_matches = watcher.match.matchlist_by_puuid(match_region, me['puuid'],start=0,count=20)
#print(my_matches)

# fetch last match detail
last_match = my_matches[0]
match_detail = watcher.match.by_id(match_region, last_match)

participants = []
for row in match_detail['info']['participants']:
    participants_row = {}
    participants_row['summonerName'] = row['summonerName']
    participants_row['individualPosition'] = row['individualPosition']
    participants_row['championName'] = row['championName']
    participants_row['champLevel'] = row['champLevel']
    participants_row['kills'] = row['kills']
    participants_row['deaths'] = row['deaths']
    participants_row['assists'] = row['assists']
    participants_row['visionScore'] = row['visionScore']
    participants_row['goldEarned'] = row['goldEarned']
    participants_row['totalMinionsKilled'] = row['totalMinionsKilled']
    participants_row['item0'] = row['item0']
    participants_row['item1'] = row['item1']
    participants_row['item2'] = row['item2']
    participants_row['item3'] = row['item3']
    participants_row['item4'] = row['item4']
    participants_row['item5'] = row['item5']
    participants_row['item6'] = row['item6']
    participants_row['win'] = row['win']
    participants_row['gameDuration'] = match_detail['info']['gameDuration']
    participants.append(participants_row)
df = pd.DataFrame(participants)
output_csv = "Last_Match.csv"
df.to_csv(output_csv)
"""
 
#print(df)
if __name__ == "__main__":
    app.run(debug=True)
