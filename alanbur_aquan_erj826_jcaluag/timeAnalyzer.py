"""
CS591
Project 2
11.2.17
timeAnalyzer.py

reads the two collections with [time, accident] data
returns correlation coefficient
"""

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import requests
import numpy as np
import random

class timeAnalyzer(dml.Algorithm):
    contributor = 'alanbur_aquan_erj826_jcaluag'
    reads = ['alanbur_aquan_erj826_jcaluag.timeAggregateNY', 'alanbur_aquan_erj826_jcaluag.timeAggregateSF']
    writes = ['timeAnalysis']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo

        repo.authenticate('alanbur_aquan_erj826_jcaluag', 'alanbur_aquan_erj826_jcaluag')          

        repo.dropCollection("timeAnalysis")
        repo.createCollection("timeAnalysis")

        timeNY = [entry['data'] for entry in repo.alanbur_aquan_erj826_jcaluag.timeAggregateNY.find()][0]
        timeSF = [entry['data'] for entry in repo.alanbur_aquan_erj826_jcaluag.timeAggregateSF.find()][0]

        SampleSize=100
        if trial:
            TrialSample=timeNY[:SampleSize]
            for i in range(SampleSize+1,len(timeNY)):
                j=random.randint(1,i)
                if j<SampleSize:
                    TrialSample[j] = timeNY[i]
        #    print('Running in trial mode')
            timeNY=TrialSample

            TrialSample=timeSF[:SampleSize]
            for i in range(SampleSize+1,len(timeSF)):
                j=random.randint(1,i)
                if j<SampleSize:
                    TrialSample[j] = timeSF[i]
        #    print('Running in trial mode')
            timeSF=TrialSample

        cov= np.corrcoef(timeNY,timeSF)[0][1]

        result={"correlation":cov}
  
        repo['alanbur_aquan_erj826_jcaluag.timeAnalysis'].insert(result, check_keys=False)
        repo['alanbur_aquan_erj826_jcaluag.timeAnalysis'].metadata({'complete':True})
       # print(repo['alanbur_aquan_erj826_jcaluag.timeAnalysis'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    @staticmethod

    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('alanbur_aquan_erj826_jcaluag', 'alanbur_aquan_erj826_jcaluag')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        #resources:
        
        #define the agent
        this_script = doc.agent('alg:alanbur_aquan_erj826_jcaluag#timeAnalyzer', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        #define the input resource
        resource = doc.entity('dat:timeAggregateNY', {'prov:label':'NY Time Aggregation', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        resource2 = doc.entity('dat:timeAggregateSF', {'prov:label':'SF Time Aggregation', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        #define the activity of taking in the resource
        action = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(action, this_script)
        doc.usage(action, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'
                  }
                  )
        doc.usage(action, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation'
                  }
                  )
        
        #define the writeout 
        output = doc.entity('dat:alanbur_aquan_erj826_jcaluag#timeAnalysis', {prov.model.PROV_LABEL:'Time Analysis of NY and SF', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(output, this_script)
        doc.wasGeneratedBy(output, action, endTime)
        doc.wasDerivedFrom(output, resource, action, action, action)
        doc.wasDerivedFrom(output, resource2, action, action, action)

        repo.logout()
                  
        return doc

# timeAnalyzer.execute()

## eof
