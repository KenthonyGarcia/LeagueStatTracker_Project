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
from config import api_key, aws_access_key_id, aws_secret_access_key
import MySQLdb.cursors
import numpy as np
import boto3
import pyotp
import qrcode
import re
import json
import pandas as pd
import os
import pyotp
import sys
import urllib.request, json
from flask_cors import CORS



#PROFILEICON_FOLDER = os.path.join('static', 'img', 'profileicon')
#ITEM_FOLDER = os.path.join('static', 'img', 'item')

app = Flask(__name__)
CORS(app)




# global variables/ ALSO REMOVE API KEY BEFORE PUSHING
#Remember to remove the API key before pushing.
#Remember to remove the API key before pushing code to github repository.

watcher = LolWatcher(api_key)

mysql = MySQL(app)
dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1', aws_access_key_id = aws_access_key_id , aws_secret_access_key = aws_secret_access_key)
s3 = boto3.client('s3', region_name = 'us-east-1', aws_access_key_id = aws_access_key_id , aws_secret_access_key = aws_secret_access_key)

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
            for k in range(len(fulllist)):
                participants = []
                ss = []
                if fulllist[k]['info']['gameMode'] == ("CLASSIC") or ("ARAM"):
                    for row in fulllist[j]['info']['participants']:
                        if (row['summonerName'].upper() == (sumname).upper()):
                            ss_row = {}
                            ss_row['Summoner Name'] = row['summonerName']
                            ss_row['Position'] = row['individualPosition']
                            ss_row['Champion Name'] = row['championName']
                            ss_row['Champion Level'] = row['champLevel']
                            ss_row['Kills'] = row['kills']
                            ss_row['Deaths'] = row['deaths']
                            ss_row['Assists'] = row['assists']
                            ss_row['Vision Score'] = row['visionScore']
                            ss_row['Gold Earned'] = row['goldEarned']
                            ss_row['Minions Killed'] = row['totalMinionsKilled']
                            ss_row['item0'] = row['item0']
                            ss_row['item1'] = row['item1']
                            ss_row['item2'] = row['item2']
                            ss_row['item3'] = row['item3']
                            ss_row['item4'] = row['item4']
                            ss_row['item5'] = row['item5']
                            ss_row['item6'] = row['item6']
                            ss_row['Win'] = row['win']
                            #participants_row['gameDuration'] = fulllist['info']['gameDuration']
                            ss.append(ss_row)
                            var = ss
                        ##############################################################################    
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

                    ssdf = pd.DataFrame(ss)
                    sscdf = []
                    for i in ssdf['Champion Name']:
                        sschampion = str(i) + '.png'
                        sschampion_file_path = 'https://league-img.s3.amazonaws.com/img/champion/' + sschampion
                        sscdf.append(path_to_image_html(sschampion_file_path))
                    ssdf['Champion Name'] = sscdf
                    ssi0 = []
                    for i in ssdf['item0']:
                        ssItem0 = str(i) +'.png'
                        ssItem0_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + ssItem0
                        ssi0.append(path_to_image_html(ssItem0_file_path))
                    ssdf['item0'] = ssi0
                    ssi1 = []
                    for i in ssdf['item1']:
                        ssItem1 = str(i) +'.png'
                        ssItem1_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + ssItem1
                        ssi1.append(path_to_image_html(ssItem1_file_path))
                    ssdf['item1'] = ssi1
                    ssi2 = []
                    for i in ssdf['item2']:
                        ssItem2 = str(i) +'.png'
                        ssItem2_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + ssItem2
                        ssi2.append(path_to_image_html(ssItem2_file_path))
                    ssdf['item2'] = ssi2
                    ssi3 = []
                    for i in ssdf['item3']:
                        ssItem3 = str(i) +'.png'
                        ssItem3_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + ssItem3
                        ssi3.append(path_to_image_html(ssItem3_file_path))
                    ssdf['item3'] = ssi3
                    ssi4 = []
                    for i in ssdf['item4']:
                        ssItem4 = str(i) +'.png'
                        ssItem4_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + ssItem4
                        ssi4.append(path_to_image_html(ssItem4_file_path))
                    ssdf['item4'] = ssi4
                    ssi5 = []
                    for i in ssdf['item5']:
                        ssItem5 = str(i) +'.png'
                        ssItem5_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + ssItem5
                        ssi5.append(path_to_image_html(ssItem5_file_path))
                    ssdf['item5'] = ssi5
                    ssi6 = []
                    for i in ssdf['item6']:
                        ssItem6 = str(i) +'.png'
                        ssItem6_file_path = 'https://league-img.s3.amazonaws.com/img/item/' + ssItem6
                        ssi6.append(path_to_image_html(ssItem6_file_path))
                    ssdf['item6'] = ssi6
                    
                    


                    ssoutput_csv = nameid+"_Match"+str(j)+".csv"
                    sscomplete_buf = StringIO()
                    ssdf.to_csv(sscomplete_buf, index=False)
                    sscomplete_buf.seek(0)
                    #s3.meta.client.upload_file('match_history'+output_csv, 'league-img', output_csv)
                    s3.put_object(Bucket="league-img", Body=sscomplete_buf.getvalue(), Key="match_history/"+ssoutput_csv)

                    sstable=[]
                    for i in range(20):
                        ssdf_obj = s3.get_object(Bucket="league-img", Key="match_history/"+nameid+"_Match"+str(i)+".csv")
                        ssdf_body = ssdf_obj['Body']
                        sscsv_string = ssdf_body.read().decode('utf-8')
                        sss3_df = pd.read_csv(StringIO(sscsv_string))
                        sstitle=sss3_df.columns.values   
                        sstables=[sss3_df.to_html(escape=False,classes='data')]
                        sstable.append(sstables)
                    
                    ssmatch0,ssmatch1,ssmatch2,ssmatch3,ssmatch4,ssmatch5,ssmatch6,ssmatch7,ssmatch8,ssmatch9,ssmatch10,ssmatch11,ssmatch12,ssmatch13,ssmatch14,ssmatch15,ssmatch16,ssmatch17,ssmatch18,ssmatch19= [e for e in sstable]
#############################################################################

                    challenges = []
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
                    df = pd.DataFrame(participants)
                    df_complete = pd.concat([df, challengeslistdf], axis = 1)
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
            """
            
            """
            
            #Reading the file from s3------------------------------------
            table=[]
            for i in range(20):
                df_obj = s3.get_object(Bucket="league-img", Key="match_history/"+nameid+"_Match"+str(i)+".csv")
                df_body = df_obj['Body']
                csv_string = df_body.read().decode('utf-8')
                s3_df = pd.read_csv(StringIO(csv_string))
                title=s3_df.columns.values   
                tables=[s3_df.to_html(escape=False,classes='data')]
                table.append(tables)
                
            match0,match1,match2,match3,match4,match5,match6,match7,match8,match9,match10,match11,match12,match13,match14,match15,match16,match17,match18,match19= [e for e in table]
            
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
            #champid_counter = 0
            #champid_to_name = []
            #with urllib.request.urlopen("http://ddragon.leagueoflegends.com/cdn/12.8.1/data/en_US/champion.json") as url:
                #champjson = json.loads(url.read().decode())
            #for i in champjson:
                #if champjson[i].key == champid[champid_counter]:
                    #champid_to_name[champid_counter] = champjson[i].id
                    #champid_counter += 1
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
            level = sumonnerLevel, tables0 = match0,tables1 = match1,tables2 =match2,tables3 =match3,tables4 =match4,tables5 =match5,tables6 =match6,
            tables7 =match7,tables8 =match8,tables9 =match9,tables10 =match10,tables11 =match11,tables12 =match12,tables13 =match13,tables14 =match14,
            tables15 =match15,tables16 =match16,tables17 =match17,tables18 =match18,tables19 =match19, titles =title, sstitles = sstitle, 
            champ_level = champlevel, champ_pts = champpoints, var = var, sstables0 = ssmatch0) #pass profile_img as variable for
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
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        code = request.form['otp_code']
        table = dynamodb.Table('users')
        response = table.query(KeyConditionExpression=Key('email').eq(email))
        items = response['Items']
        sec_key = items[0]['sec_key']
        otp_gen = pyotp.TOTP(sec_key)
        summonername = items[0]['SummonerName']
        username = items[0]['username']
        if password == items[0]['password']:
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
        sec_key = pyotp.random_base32() 
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
    sec_key = items[0]['sec_key']
    otp_gen = pyotp.TOTP(sec_key)
    auth_str = otp_gen.provisioning_uri(name=email, issuer_name=('RiftTracker'))
    qrimg0 = 'https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl=' + auth_str
    if request.method == "POST":
        msg = ''
    return render_template('authentication.html', msg = msg, qrimg = qrimg0)

if __name__ == "__main__":
    app.run(debug=True)
