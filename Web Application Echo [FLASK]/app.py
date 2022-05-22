from flask import Flask,render_template,request
import time
import os
import psutil
import sys
import pandas as pd
import csv
import random
from flask import request
import difflib
import coverpy
import numpy as np
from scipy import spatial
app = Flask(__name__)

#@app.route("/")
#@app.route("/home")
from scipy.spatial import distance
def compute_distances(probabilities,current_vector):

  probabilities = [eval(x) for x in probabilities]

  current_vector = eval(current_vector)
  print(current_vector)
  cosine_similarity = [[compute_distance(x,current_vector),index] for index,x in enumerate(probabilities)]
  #print(len(probabilities),len(current_vector),len(cosine_similarity),len(cosine_similarity[0]))
  cosine_similarity.sort(key=lambda x: (x[0]),reverse=True)

  answer = [x[1] for x in cosine_similarity[:5]]
  return answer

import math
def compute_distance(array1,array2):
  res = 0
  for i in range(len(array1)):
    res+=(array1[i]-array2[i])**2
  return math.sqrt(res)

@app.route("/")
@app.route("/home")
def home():


    return render_template("display_page.html")

@app.route("/mainrecommendation", methods = ['POST','GET'])
def mainrecommendation():
    data = []
    query = request.args["songName"]
    query = query.replace("~", " ")
    data.append(query)
    df = pd.read_csv('models/prob_vec.csv')
    df = df[df['Class']!="Funny"]
    df.reset_index(inplace=True)
    sname = df['Song']
    indx = -1
    sname = [e.lower() for e in sname]
    query = query.lower()
    #print("sname", sname[2])
    for x in range(len(sname)):
        if sname[x] == query:
            indx = x
            break
    probabilities = list(df['probability_vector'])
    indexes = compute_distances(probabilities,probabilities[indx])
    print(indexes)
    rec_songs = df.iloc[indexes]
    print(rec_songs.values.tolist())

    ans = []
    for x in rec_songs.values.tolist():
        temp = []
        temp.append(x[2])
        temp.append(x[3])
        temp.append(x[4])

        query = x[3].replace(" ", "~")
        temp.append(query)

        ans.append(temp)


    #print(indx)
    #print(df.iloc[indx])
    #print("_______")
    #print(query)
    #print(len(query),query)
    return render_template("mainrecommendation.html", data = data, thisdata = ans)

@app.route("/index", methods = ['GET', 'POST'])
def data():

    df = pd.read_csv('cleaned_lyrics.csv')
    #df = df.sample(n=50)
    artistName = df['Artist']
    songName = df['Song']
    className = df['Class']
    madesongname = []

    for x in songName:
        temp = x.split(" ")
        madesongname.append("~".join(temp))

    ans = []
    for x in range(len(artistName)):
        ans.append([artistName[x], songName[x], className[x],madesongname[x]])
    random.shuffle(ans)
    return render_template('index.html', data = ans[:50])

def match(arr1,arr2):
    #print(len(set(arr1).intersection(set(arr2))))
    arr1 = sorted(arr1) ## query
    arr2 = sorted(arr2) ## song name checking
    match_count = 0
    ll = min(len(arr1), len(arr2))

    for c in range(ll):
        w1 = arr1[c]
        w2 = arr2[c]

        minlen = min(len(w1), len(w2))
        thiscount = 0
        for z in range(minlen):
            if w1[z] == w2[z]:
                thiscount+=1

        if thiscount >= max(len(w1) , len(w2)) * 0.6:
            match_count+=1
    return match_count
    ##return len(set(arr1).intersection(set(arr2)))

@app.route("/searchresult", methods = ['POST', 'GET'])
def find_search_results():
    ##artist_name = request.form.get("artistName")
    query = request.form.get("songName")
    query.lower()

    all_songs_list = pd.read_csv('cleaned_lyrics.csv')
    aname = all_songs_list['Artist']
    sname = all_songs_list['Song']
    cname = all_songs_list['Class']
    sname = [x.lower() for x in sname]
    matches = []
    query_elems = query.split(" ")
    for x in range(len(sname)):
        comp = sname[x].split(" ")
        cnt = match(query_elems, comp)
        if cnt >=1:
            print("done")
            matches.append([cnt,x])

    matches = sorted(matches, key = lambda x:x[0])

    res = []
    matches = matches[:min(len(matches), 10)]
    for y,x in matches:
        res.append([aname[x], sname[x], cname[x]])
    return render_template('searchresults.html', match_results = res)
if __name__ == '__main__':
    app.run(debug = True, port = 5001)
#@app.route("/result", methods = ['POST','GET'])
#def result():##this is where we will make all the predictions
