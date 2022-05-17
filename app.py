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
from io import StringIO
from PIL import Image
import MySQLdb.cursors
import numpy as np
import boto3
import pyotp
import qrcode
import json
import pandas as pd
import os
import pyotp
import sys
from flask_cors import CORS
from leaguenames import leaguenames 




app = Flask(__name__)
CORS(app)




# global variables/ ALSO REMOVE API KEY BEFORE PUSHING


watcher = LolWatcher(api_key)

mysql = MySQL(app)
dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1', aws_access_key_id = aws_access_key_id , aws_secret_access_key = aws_secret_access_key)
s3 = boto3.client('s3', region_name = 'us-east-1', aws_access_key_id = aws_access_key_id , aws_secret_access_key = aws_secret_access_key)


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
            last_match = summoner_matches#selects the last match on the account
            #match_detail = watcher.match.by_id(match_region, last_match)
            i=0
            fulllist = []
            for row in last_match:
                match_detail = watcher.match.by_id(match_region, last_match[i])
                fulllist.append(match_detail)
                i+=1
            
            j = 0
            k=0
            for k in range(len(fulllist)):#loops through all 20 matches and creates 20 csv files numbered from 0-19 which are sent to the s3 server
                participants = []
                if fulllist[k]['info']['gameMode'] == ("CLASSIC") or ("ARAM"):
                    for row in fulllist[j]['info']['participants']:
                        participants_row = {}
                        participants_row['Summoner Name'] = row['summonerName']
                        participants_row['Position'] = row['individualPosition']
                        participants_row['Champion Name'] = row['championName']
                        participants_row['Champion Level'] = row['champLevel']
                        participants_row['Kills'] = row['kills']
                        participants_row['Deaths'] = row['deaths']
                        participants_row['Assists'] = row['assists']
                        participants_row['Vision Score'] = row['visionScore']
                        participants_row['Gold Earned'] = row['goldEarned']
                        participants_row['Minions Killed'] = row['totalMinionsKilled']
                        participants_row['item0'] = row['item0']
                        participants_row['item1'] = row['item1']
                        participants_row['item2'] = row['item2']
                        participants_row['item3'] = row['item3']
                        participants_row['item4'] = row['item4']
                        participants_row['item5'] = row['item5']
                        participants_row['item6'] = row['item6']
                        participants_row['Win'] = row['win']
                        #participants_row['gameDuration'] = fulllist['info']['gameDuration']
                        participants.append(participants_row)
                    
                    
                    
                    challenges = []#creates a challeges dataframe that will take sub dictionary challenges from the participants dictionary
                    for row in fulllist[j]['info']['participants']:
                        challenges_row = {}
                        challenges_row['challenges'] = row['challenges']
                        challenges.append(challenges_row)
                    challengesdf = pd.DataFrame(challenges)

                    challengeslist = []
                    for row in challengesdf['challenges']:
                        challengeslist_row = {}
                        challengeslist_row['kda'] = row['kda']
                        challengeslist_row['killParticipation'] = row['killParticipation']
                        challengeslist.append(challengeslist_row)
                    challengeslistdf = pd.DataFrame(challengeslist)
                    challengeslistdf['kda'] = [round(x,2) for x in challengeslistdf['kda']]
                    challengeslistdf['killParticipation'] = [round(x,2) for x in challengeslistdf['killParticipation']]
                    df = pd.DataFrame(participants)
                    df_complete = pd.concat([df, challengeslistdf], axis = 1)
                    #Renaming positions in the dataframe to the positions they should be called
                    df_complete['Position'] = ['Normal' if element == ('Invalid') else element for element in df_complete['Position']]
                    df_complete['Position'] = ['Top' if element == ('TOP') else element for element in df_complete['Position']]
                    df_complete['Position'] = ['Mid' if element == ('MIDDLE') else element for element in df_complete['Position']]
                    df_complete['Position'] = ['Bottom' if element == ('BOTTOM') else element for element in df_complete['Position']]
                    df_complete['Position'] = ['Jungle' if element == ('JUNGLE') else element for element in df_complete['Position']]
                    df_complete['Position'] = ['Support' if element == ('UTILITY') else element for element in df_complete['Position']]
                    
                    #Champion and item loops to add image files into dataframe
                    championdf= []
                    for i in df_complete['Champion Name']:
                        champion = str(i) +'.png'
                        champion_file_path = 'https://league-img.s3.amazonaws.com/img/champion/' + champion
                        championdf.append(path_to_image_html(champion_file_path))#appends the paths to a new dataframe
                    df_complete['Champion Name'] = championdf
                    championicon = df_complete['Champion Name'].to_list() #makes a list of paths for the champion images
                    item0df= []
                    for i in df_complete['item0']:
                        Item0 = str(i) +'.png'
                        Item0_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item0
                        item0df.append(path_to_image_html(Item0_file_path))
                    df_complete['item0'] = item0df
                    Item0icon = df_complete['item0'].to_list()
                    item1df= []
                    for i in df_complete['item1']:
                        Item1 = str(i) +'.png'
                        Item1_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item1
                        item1df.append(path_to_image_html(Item1_file_path))
                    df_complete['item1'] = item1df
                    Item1icon = df_complete['item1'].to_list()
                    item2df= []
                    for i in df_complete['item2']:
                        Item2 = str(i) +'.png'
                        Item2_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item2
                        item2df.append(path_to_image_html(Item2_file_path))
                    df_complete['item2'] = item2df
                    Item2icon = df_complete['item2'].to_list()
                    item3df= []
                    for i in df_complete['item3']:
                        Item3 = str(i) +'.png'
                        Item3_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item3
                        item3df.append(path_to_image_html(Item3_file_path))
                    df_complete['item3'] = item3df
                    Item3icon = df_complete['item3'].to_list()
                    item4df= []
                    for i in df_complete['item4']:
                        Item4 = str(i) +'.png'
                        Item4_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item4
                        item4df.append(path_to_image_html(Item4_file_path))
                    df_complete['item4'] = item4df
                    Item4icon = df_complete['item4'].to_list()
                    item5df= []
                    for i in df_complete['item5']:
                        Item5 = str(i) +'.png'
                        Item5_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item5
                        item5df.append(path_to_image_html(Item5_file_path))
                    df_complete['item5'] = item5df
                    Item5icon = df_complete['item5'].to_list()
                    item6df= []
                    for i in df_complete['item6']:
                        Item6 = str(i) +'.png'
                        Item6_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + Item6
                        item6df.append(path_to_image_html(Item6_file_path))
                    df_complete['item6'] = item6df
                    Item6icon = df_complete['item6'].to_list()
                    output_csv = nameid+"_Match"+str(j)+".csv"
                    complete_buf = StringIO()
                    df_complete.to_csv(complete_buf, index=False)
                    complete_buf.seek(0)
                    #s3.meta.client.upload_file('match_history'+output_csv, 'league-img', output_csv)
                    s3.put_object(Bucket="league-img", Body=complete_buf.getvalue(), Key="match_history/"+output_csv)
                    j+=1
                
            """
            #turning the dataframe columns to a list for frontend use.
            summonerName = df_complete['Summoner Name'].to_list() #Creates a list for each dataframe column making it easier for frontend to use the values of the variables.
            indPosition = df_complete['Position'].to_list()
            kills = df_complete['Kills'].to_list()
            deaths = df_complete['Deaths'].to_list()
            assists = df_complete['Assists'].to_list()
            killParticipation = df_complete['killParticipation'].to_list()
            kda = df_complete['kda'].to_list()
            visionScore = df_complete['Vision Score'].to_list()
            goldEarned = df_complete['Gold Earned'].to_list()
            creepScore = df_complete['Minions Killed'].to_list()
            win = df_complete['Win'].to_list()
            gameDuration = df_complete['Game Duration'].to_list()
            """
            #GameDuration conversion
            """
            gametime = (gameDuration[0])#only need
            mintues = int(gametime/60)
            seconds = gametime%60
            match_time = str(mintues)+"m"+str(seconds)+'s'
            """
            
            #Reading the files from s3------------------------------------
            table=[]
            snapshot=[]
            for i in range(20):#loops 20 times for all 20 files that are stored on the s3 server
                df_obj = s3.get_object(Bucket="league-img", Key="match_history/"+nameid+"_Match"+str(i)+".csv")
                df_body = df_obj['Body']
                csv_string = df_body.read().decode('utf-8')
                s3_df = pd.read_csv(StringIO(csv_string))
                ss = (s3_df.loc[s3_df['Summoner Name'] == nameid])#looks for the row where the players name is equal to the summoner name that is being searched.
                snapshots = [ss.to_html(escape=False,classes='data')]
                title=s3_df.columns.values
                tables=[s3_df.to_html(escape=False,classes='data')]
                table.append(tables)
                snapshot.append(snapshots)#appends the one row dataframe to a list that contains matches 0-19
                
            
            
            #Player top mastery champs----------------
            top_champ_mastery = watcher.champion_mastery.by_summoner('NA1', summonerdict['id'])

            champs = []
            for row in top_champ_mastery[0:3]:
                champ_row = {}
                champ_row['championId'] = row['championId']
                champ_row['championLevel'] = row['championLevel']
                champ_row['championPoints'] = row['championPoints']
                champs.append(champ_row)
            masterydf = pd.DataFrame(champs)
            champid = masterydf['championId'].to_list()
            #champid needs to be converted to name
            for x in range(len(champid)):
                convert = leaguenames(champid[x])
                champid[x] = convert
            champlevel = masterydf['championLevel'].to_list()
            champpoints = masterydf['championPoints'].to_list()
            

            #-----------------------------------------
            regions = ['NA1', 'EUW1', 'EUN1', 'BR1', 'LA1', 'LA2', 'OCE', 'RU1', 'TR1', 'JP1', 'KR'] #region codes
            name = str(nameid)
            sumonnerLevel = str(Levelid)
            profile_icon_id = str(imgid) +'.png'
            profileicon_file_path = 'https://league-img.s3.amazonaws.com/img/profileicon/' + profile_icon_id
            #return redirect(url_for("summoner", pi = profileicon_file_path, ii = Item0_file_path, username = sumname, lev = sumonnerLevel, tb = [df.to_html(classes='data')], title = df.columns.values ))
            return render_template('summoner.html',test = top_champ_mastery,profile_img = profileicon_file_path, item0_img = Item0icon, 
            item1_img = Item1icon, item2_img = Item2icon, item3_img = Item3icon, item4_img = Item4icon, item5_img = Item5icon, 
            item6_img = Item6icon, champion_img = championicon, name = name, region = regions, champid = champid,
            level = sumonnerLevel, snaptable0 = snapshot[0],snaptable1 = snapshot[1], snaptable2 = snapshot[2],snaptable3 = snapshot[3], snaptable4 = snapshot[4],
            snaptable5 = snapshot[5], snaptable6 = snapshot[6], snaptable7 = snapshot[7],snaptable8 = snapshot[8], snaptable9 = snapshot[9],snaptable10 = snapshot[10],
            snaptable11 = snapshot[11],snaptable12 = snapshot[12],snaptable13 = snapshot[13],snaptable14 = snapshot[14],snaptable15 = snapshot[15],snaptable16 = snapshot[16],
            snaptable17 = snapshot[17],snaptable18 = snapshot[18],snaptable19 = snapshot[19],
            tables0 = table[0],tables1 = table[1],tables2 =table[2],tables3 =table[3],tables4 =table[4],tables5 =table[5],tables6 =table[6],
            tables7 =table[7],tables8 =table[8],tables9 =table[9],tables10 =table[10],tables11 =table[11],tables12 =table[12],tables13 =table[13],tables14 =table[14],
            tables15 =table[15],tables16 =table[16],tables17 =table[17],tables18 =table[18],tables19 =table[19], titles =title, 
            champ_level = champlevel, champ_pts = champpoints, champ_name = champid) #pass profile_img as variable for
            #note: change index.html(search page) to summoner.html(result page)
        except: 
            return redirect(url_for('error'))
            #return render_template('notFound.html')
    else:
        return render_template('index.html') 

@app.route('/summoner/<string:name>', methods=['GET', 'POST'])
def summoner(sN, pi, ii, lev, tb, title):
    return render_template('summoner.html', profile_img = pi, item0_img = ii,  name = sN, level = lev, tables= tb, titles= title) #pass profile_img as variable for
    
 
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
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:#requests email,password,and a one time password
        email = request.form['email']
        password = request.form['password']
        code = request.form['otp_code']
        table = dynamodb.Table('users')
        response = table.query(KeyConditionExpression=Key('email').eq(email))
        items = response['Items']
        sec_key = items[0]['sec_key']#takes the security key that is used to generate the one time password code
        otp_gen = pyotp.TOTP(sec_key)
        summonername = items[0]['SummonerName']
        username = items[0]['username']
        if password == items[0]['password']:#if the password inputed and the password stored are the same then it will check if the code given is the same as the generated code
            if otp_gen.now() == code:
                msg = 'Logged in successfully!'
                return redirect(url_for('profile', msg = msg, username = username, summonername = summonername))
            elif otp_gen.now() != code:
                msg = 'Incorrect Authentication Code try again'
                return render_template('login.html', msg = msg)
    return render_template('login.html', msg = msg)

#profile Page
@app.route('/profile', methods =['GET', 'POST'])
def profile():
    username = request.args.get('username', None)
    summonername = request.args.get('SummonerName', None)
    df_obj = s3.get_object(Bucket="league-img", Key="match_history/"+summonername+"_Match"+str(0)+".csv")
    df_body = df_obj['Body']
    csv_string = df_body.read().decode('utf-8')
    s3_df = pd.read_csv(StringIO(csv_string))
    return render_template('profile.html', username = username, summonername = summonername, tables=[s3_df.to_html(escape=False,classes='data')], titles=s3_df.columns.values)
    

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
        #Google Authenticator QrCode generator
        sec_key = pyotp.random_base32() #Security key is stored into the DynamoDB database for when a code needs to be generated for the login stage
        table.put_item(
            Item={
                'username': username,
                'SummonerName' : summonername,
                'email' : email,
                'password' : password,
                'sec_key' : sec_key,
            }   
        )
        msg = 'You have successfully registered, please scan the qrcode'
        return redirect(url_for('authentication', msg = msg, email = email))
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

#Authentication Page
@app.route('/Authentication', methods =['GET', 'POST'])
def authentication():
    msg = ''
    email = request.args.get('email', None)
    email0 = email
    table = dynamodb.Table('users')
    response = table.query(KeyConditionExpression=Key('email').eq(str(email0)))
    items = response['Items']
    sec_key = items[0]['sec_key']#pulls the security key from DynamoDB 
    otp_gen = pyotp.TOTP(sec_key)
    auth_str = otp_gen.provisioning_uri(name=email, issuer_name=('RiftTracker'))
    qrimg0 = 'https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl=' + auth_str
    if request.method == "POST":
        msg = ''
    return render_template('authentication.html', msg = msg, qrimg = qrimg0)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)