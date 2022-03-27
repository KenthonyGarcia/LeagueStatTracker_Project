"""
Created on Mon Feb 21 10:57:41 2022

@author: kenth
"""
from riotwatcher import LolWatcher, ApiError
from IPython.display import display
from IPython.core.display import HTML
from flask import Flask, request, render_template, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from boto3.dynamodb.conditions import Key, Attr
from flask_mysqldb import MySQL
from PIL import Image
import MySQLdb.cursors
import boto3
import pyotp
import qrcode
import re
import json
import pandas as pd
import os



#PROFILEICON_FOLDER = os.path.join('static', 'img', 'profileicon')
#ITEM_FOLDER = os.path.join('static', 'img', 'item')

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your password'
app.config['MYSQL_DB'] = 'login'

# global variables/ ALSO REMOVE API KEY BEFORE PUSHING
api_key = 'RGAPI-6b771f45-1da8-4cf0-a5d5-9e65f01ff49a'#Remember to remove the API key before pushing.
#Remember to remove the API key before pushing code to github repository.


watcher = LolWatcher(api_key)

mysql = MySQL(app)
dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1', aws_access_key_id ='AKIAWANQWOMS5FXZBOM5', aws_secret_access_key = '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', aws_session_token = '')

#----dropdown for regions
#@app.route('/', methods = ['GET'])
#def dropdown():
#    regions = ['NA1', 'EUW1', 'EUN1', 'BR1', 'LA1', 'LA2', 'OCE', 'RU1', 'TR1', 'JP1', 'KR'] #region codes
#    return render_template('index.html', regions = regions) #regions is the dropdown menu variable name
#----
def path_to_image_html(path):
    html_function = '<img src="'+ path + '" width="60">'
    return html_function

@app.route('/', methods=['POST', 'GET']) #main page that will be loaded first.
def Main():
    if request.method == 'POST':
        sumname = request.form['SummonerName'] #gets summoner name from inputed text.
        #profile = Summoner(name=sumname)
        region = 'NA1' #for now we will focus on the North American server.

        if region == 'NA1':
            match_region = 'AMERICAS'
        elif region == 'BR1':
            match_region = 'AMERICAS'
        elif region == 'LA1':
            match_region = 'AMERICAS'
        elif region == 'LA2':
            match_region = 'AMERICAS'
        elif region == 'OC1':
            match_region = 'AMERICAS'
        elif region == 'KR':
            match_region = 'ASIA'
        elif region == 'JP1':
            match_region = 'ASIA'
        elif region == 'EUN1':
            match_region = 'EUROPE'
        elif region == 'EUW1':
            match_region = 'EUROPE'
        elif region == 'RU':
            match_region = 'EUROPE'
        else:
            match_region = 'EUROPE'
        
        try:
            summonerdict = watcher.summoner.by_name(region, sumname) #pulls summoner data from riot api into a dictionary
            subsets_needed = ['name', 'profileIconId', 'summonerLevel'] #for now all we need is name, profileIconId, and summonerLevel.
            demodict = {key: summonerdict[key] for key in subsets_needed} #separates the keys we need form the dictionary
            nameid = demodict['name']
            imgid = demodict['profileIconId']
            Levelid = demodict['summonerLevel']
            
            summoner_matches = watcher.match.matchlist_by_puuid(match_region, summonerdict['puuid'],start=0,count=20)#Brings up the 20 most recent matches.
            last_match = summoner_matches[0]#selects the last match on the account
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
            challenges = []
            for row in match_detail['info']['participants']:
                challenges_row = {}
                challenges_row['challenges'] = row['challenges']
                challenges.append(challenges_row)
            challengesdf = pd.DataFrame(challenges)

            challenges = []
            for row in challengesdf['challenges']:
                challenges_row = {}
                challenges_row['killParticipation'] = row['killParticipation']
                challenges.append(challenges_row)
            challengeslistdf = pd.DataFrame(challenges)
            
            #turning the dataframe columns to a list for frontend use.
            summonerName = df['summonerName'].to_list() #Creates a list for each dataframe column making it easier for frontend to use the values of the variables.
            indPosition = df['individualPosition'].to_list()
            kills = df['kills'].to_list()
            deaths = df['deaths'].to_list()
            assists = df['assists'].to_list()
            killParticipation = challengeslistdf['killParticipation'].to_list()
            visionScore = df['visionScore'].to_list()
            goldEarned = df['goldEarned'].to_list()
            creepScore = df['totalMinionsKilled'].to_list()
            win = df['win'].to_list()
            gameDuration = df['gameDuration'].to_list()
            
            #KDA Calculation
            KA =[i + j for i, j in zip(kills, assists)]
            KDA_raw =[i / j for i, j in zip(KA, deaths)]
            KDA_rounded = [round(num, 2) for num in KDA_raw]
            
            #GameDuration conversion
          
            
            #sN = summonerName, iP = indPosition, K = kills, D = deaths, A = assists, vS =  visionScore, gE = goldEarned, cS = creepScore, W = win, gD = gameDuration
            
            
            #creating lists of image paths for items and champions
            championdf= []
            for i in df['championName']:
                champion = str(i) +'.png'
                champion_file_path = 'https://league-img.s3.amazonaws.com/img/champion/' + champion
                championdf.append(path_to_image_html(champion_file_path))#appends the paths to a new dataframe
            df['championName'] = championdf
            championicon = df['championName'].to_list() #makes a list of paths for the champion images
            
            item0df= []
            for i in df['item0']:
                Item0 = str(i) +'.png'
                #Item0_file_path = os.path.join(app.config['UPLOAD_FOLDER'], Item0)
                Item0_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item0
                item0df.append(path_to_image_html(Item0_file_path))
            df['item0'] = item0df
            Item0icon = df['item0'].to_list()
            item1df= []
            for i in df['item1']:
                Item1 = str(i) +'.png'
                #Item1_file_path = os.path.join(app.config['UPLOAD_FOLDER'], Item1)
                Item1_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item1
                item1df.append(path_to_image_html(Item1_file_path))
            df['item1'] = item1df
            Item1icon = df['item1'].to_list()
            item2df= []
            for i in df['item2']:
                Item2 = str(i) +'.png'
                #Item0_file_path = os.path.join(app.config['UPLOAD_FOLDER'], Item0)
                Item2_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item2
                item2df.append(path_to_image_html(Item2_file_path))
            df['item2'] = item2df
            Item2icon = df['item2'].to_list()
            item3df= []
            for i in df['item3']:
                Item3 = str(i) +'.png'
                #Item0_file_path = os.path.join(app.config['UPLOAD_FOLDER'], Item0)
                Item3_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item3
                item3df.append(path_to_image_html(Item3_file_path))
            df['item3'] = item3df
            Item3icon = df['item3'].to_list()
            item4df= []
            for i in df['item4']:
                Item4 = str(i) +'.png'
                #Item0_file_path = os.path.join(app.config['UPLOAD_FOLDER'], Item0)
                Item4_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item4
                item4df.append(path_to_image_html(Item4_file_path))
            df['item4'] = item4df
            Item4icon = df['item4'].to_list()
            item5df= []
            for i in df['item5']:
                Item5 = str(i) +'.png'
                #Item0_file_path = os.path.join(app.config['UPLOAD_FOLDER'], Item0)
                Item5_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item5
                item5df.append(path_to_image_html(Item5_file_path))
            df['item5'] = item5df
            Item5icon = df['item5'].to_list()
            item6df= []
            for i in df['item6']:
                Item6 = str(i) +'.png'
                #Item0_file_path = os.path.join(app.config['UPLOAD_FOLDER'], Item0)
                Item6_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item6
                item6df.append(path_to_image_html(Item6_file_path))
            df['item6'] = item6df
            Item6icon = df['item6'].to_list() 
            
            name = str(nameid)
            sumonnerLevel = str(Levelid)
            profile_icon_id = str(imgid) +'.png'
            #profileicon_file_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_icon_id)
            profileicon_file_path = 'https://league-img.s3.amazonaws.com/img/profileicon/' + profile_icon_id
            #return demodict
            #user = request.form['content']
            #return redirect(url_for("summoner", pi = profileicon_file_path, ii = Item0_file_path, username = sumname, lev = sumonnerLevel, tb = [df.to_html(classes='data')], title = df.columns.values ))
            return render_template('summoner.html', sN = summonerName, iP = indPosition, K = kills, D = deaths, A = assists, KDA = KDA_rounded, kP = killParticipation, vS =  visionScore, gE = goldEarned, cS = creepScore, W = win, gD = gameDuration, profile_img = profileicon_file_path, item0_img = Item0icon, item1_img = Item1icon, item2_img = Item2icon, item3_img = Item3icon, item4_img = Item4icon, item5_img = Item5icon, item6_img = Item6icon, champion_img = championicon, name = name, level = sumonnerLevel, tables=[df.to_html(escape=False,classes='data')], titles=df.columns.values) #pass profile_img as variable for
            #note: change index.html(search page) to summoner.html(result page)
        except:
            return render_template('notFound.html')
            #return render_template('notFound.html')
    else:
        return render_template('index.html') 

@app.route('/summoner/<string:name>', methods=['GET', 'POST'])
def summoner(sN, pi, ii, lev, tb, title):
    return render_template('summoner.html', profile_img = pi, item0_img = ii,  name = sN, level = lev, tables= tb, titles= title) #pass profile_img as variable for
    #user1 = request.form.get['Username']
    #region1 = request.form.get['region']
    """
    summonerdf = watcher.summoner.by_name(region, name)
    summonerdf['summonerLevel']
    """

#error Page
@app.route('/error', methods=['GET', 'POST']) #main page that will be loaded first.
def error():
    if request.method == "POST":
        return redirect(url_for("Main"))
    return render_template('notFound.html')

#login Page
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        table = dynamodb.Table('users')
        response = table.query(KeyConditionExpression=Key('email').eq(email))
        items = response['Items']
        username = items[0]['username']
        if password == items[0]['password']:
            msg = 'Logged in successfully !'
            return render_template('profile.html', msg = msg, username = username)
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        summonername = request.form['SummonerName']
        email = request.form['email']
        password = request.form['password']
        table = dynamodb.Table('users')
        
        table.put_item(
            Item={
                'username': username,
                'SummonerName' : summonername,
                'email' : email,
                'password' : password,
            }   
        )
        #Google Authenticator QrCode generator
        sec_key = pyotp.random_base32()
        otp_gen = pyotp.TOTP(sec_key)
        auth_str = otp_gen.provisioning_uri(name=email, issuer_name=('RiftTracker'))
        qrimg0 = qrcode.make(auth_str)
        msg = 'You have successfully registered, please log in to your account!'
        return render_template('login.html', msg = msg, qrimg= qrimg0 )
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

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
