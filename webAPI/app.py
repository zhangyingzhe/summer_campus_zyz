from __future__ import print_function

from flask import Flask
import json
from watson_developer_cloud import LanguageTranslationV2 as LanguageTranslation
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3
from watson_developer_cloud import ToneAnalyzerV3
from cassandra.cluster import Cluster
import sys
from random import random
from operator import add

from pyspark.sql import SparkSession

app = Flask(__name__)
@app.route("/")  

def Image_design():

    visual_recognition = VisualRecognitionV3('2016-05-20',  api_key='1c5c0cf7321c6c8712c162f7b2153ae69364c974')

    with open(join(dirname(__file__), '11.png'), 'rb') as image_file:
        vs = json.dumps(visual_recognition.recognize_text(images_file=image_file), indent=2)
 
    text1=json.loads(vs)
    text1=text1["images"][0]["text"]
    text1 = json.dumps(text1,indent = 2)
    text1 = text1.replace('\\n',' ')
    text1 = text1.replace('\"',' ')

    f1 = open('/home/user/Documents/web/image.txt','w')
    f1.write(text1)
    f1.close()

    tone = tone_analyze(text1)
    cnt = wordcount()
    eslang = translations(text1)
    do_with_cassandra(vs,text1,eslang,tone)
    return '<p>IMAGE IDENTIFY: '+vs +'</p>' + '<p>Spanish: '+eslang+'</p>'+ '<p>English: '+text1+'</p>'+ '<p>Word count: '+cnt+'</p>'+'<p>TONE: '+tone+'</p>'

def tone_analyze(k):
    tone_analyzer = ToneAnalyzerV3(
        username='d9b396b9-57f4-4ef4-aa5e-a2e51d89cd43',
        password='OTFCSbRvtqrR',
        version='2016-05-19 ')

    return json.dumps(tone_analyzer.tone(text = k), indent=2)

def translations(trantext):
	language_translation = LanguageTranslation(
        username='b869542b-87b7-4d87-ae68-615d0eab46fb', 
        password='dWoKpFCDjSat')
    
	translation1 =  language_translation.translate(
		text=trantext, 
		source='en', 
        target='es')

	return translation1


def wordcount():
    spark = SparkSession\
        .builder\
        .appName("PythonWordCount")\
        .getOrCreate()

    lines = spark.read.text('/home/user/Documents/web/image.txt').rdd.map(lambda r: r[0])
    f2 = open('/home/user/Documents/web/image.txt')
    print('------------------------------------------------------------')
    print (f2.read())
    print('------------------------------------------------------------')
    counts = lines.flatMap(lambda x: x.split(' ')) \
                  .map(lambda x: (x, 1)) \
                  .reduceByKey(add)
    output = counts.collect()
    print (output)
    aa = json.dumps(output)
 
    for (word, count) in output:

        print("%s: %i" % (word, count))
    #spark.stop()
    return aa

def do_with_cassandra(_vs,_en,_es,_tone):
    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect()
    session.execute('USE mykeyspace')
    session.execute(
        """
        INSERT INTO example (vs,en,es,tone)
        VALUES (%s,%s,%s,%s)
        """,
        (_vs,_en,_es,_tone)
    )


@app.route("/analyze")  
def tone_analyze1():
   tone_analyzer = ToneAnalyzerV3(
        username='d9b396b9-57f4-4ef4-aa5e-a2e51d89cd43',
        password='OTFCSbRvtqrR',
        version='2016-05-19 ')

   f = open('analyze.txt','r')
   content = f.read()
   return json.dumps(tone_analyzer.tone(text = content), indent=2)

@app.route("/translation")  
def translation():
    language_translation = LanguageTranslation(
        username='b869542b-87b7-4d87-ae68-615d0eab46fb', 
        password='dWoKpFCDjSat')

    f1 = open('/home/user/Documents/web/trans.txt','r')
    content1 = f1.read()
    eslang =  language_translation.translate(
        text=content1, 
        source='en', 
        target='es')

    return  '<p>CONTENT: '+content1+'</p>'+'<p>TRANLATION: '+eslang+'</p>'

@app.route("/test")  
def test():

    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect()
    session.execute('USE mykeyspace')
    se = session.execute("SELECT * from example")

    for kk in se:
        #cnt = test_spark(kk.en)
        return  '<p>IMAGE IDENTIFY: '+kk.vs +'</p>' + '<p>Spanish: '+kk.es+'</p>'+ '<p>English: '+kk.en+'</p>'+'<p>TONE: '+kk.tone+'</p>'

@app.route("/testspark") 
def test_spark():
    spark = SparkSession\
        .builder\
        .appName("PythonWordCount")\
        .getOrCreate()

    lines = spark.read.text('/home/user/Documents/web/image.txt').rdd.map(lambda r: r[0])
    counts = lines.flatMap(lambda x: x.split(' ')) \
                  .map(lambda x: (x, 1)) \
                  .reduceByKey(add)
    output = counts.collect()
    aa = json.dumps(output)
    for (word, count) in output:

        print("%s: %i" % (word, count))
    #spark.stop()
    return aa

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
