import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import ast



class getData(dml.Algorithm):

    contributor = 'jdbrawn_slarbi'
    reads = []
    writes = ['jdbrawn_slarbi.entertain',
              'jdbrawn_slarbi.food']

    @staticmethod
    def execute(trial = False):
        
        startTime = datetime.datetime.now()
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('jdbrawn_slarbi', 'jdbrawn_slarbi')
    

        cred = dml.auth
        
        dataSets = {
            "entertain": 'https://data.cityofboston.gov/resource/cz6t-w69j.json',
            "food":'https://data.cityofboston.gov/resource/fdxy-gydq.json'
        }

        for key in dataSets:  
            url = dataSets[key]
            response = urllib.request.urlopen(url).read().decode("utf-8")
            r = json.loads(response) 

            repo.dropCollection(key)
            repo.createCollection(key)
            repo['jdbrawn_slarbi.'+key].insert_many(r)
            repo['jdbrawn_slarbi.'+key].metadata({'complete':True})
        
    
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
        repo.authenticate('jdbrawn_slarbi', 'jdbrawn_slarbi')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/jdbrawn_slarbi') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/jdbrawn_slarbi') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('bdp1', 'https://data.cityofboston.gov/resource/')


        this_script = doc.agent('alg:jdbrawn_slarbi#getData', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})

        resource1 = doc.entity('bdp:cz6t-w69j', {'prov:label':'Entertainment Data', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_entertainment_data = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_entertainment_data, this_script)
        doc.usage(get_entertainment_data, resource1, startTime, None,
                {prov.model.PROV_TYPE:'ont:Retrieval',
                #'ont:Query':''
                }
                )
        
        resource2 = doc.entity('bdp1:fdxy-gydq', {'prov:label':'Food License Data', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_food_license = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_food_license, this_script)
        doc.usage(get_food_license, resource2, startTime, None,
                {prov.model.PROV_TYPE:'ont:Retrieval'
                #'ont:Query':''
                }
                )



        entertainment_data = doc.entity('dat:jdbrawn_slarbi#entertain', {prov.model.PROV_LABEL:'Entertainment Data', prov.model.PROV_TYPE:'ont:DataSet', 'ont:Extension':'json'})
        doc.wasAttributedTo(entertainment_data, this_script)
        doc.wasGeneratedBy(entertainment_data, get_entertainment_data, endTime)
        doc.wasDerivedFrom(entertainment_data, resource1, get_entertainment_data, get_entertainment_data, get_entertainment_data)

        food_license = doc.entity('dat:jdbrawn_slarbi#food', {prov.model.PROV_LABEL:'Food License Data', prov.model.PROV_TYPE:'ont:DataSet', 'ont:Extension':'json'})
        doc.wasAttributedTo(food_license, this_script)
        doc.wasGeneratedBy(food_license, get_food_license, endTime)
        doc.wasDerivedFrom(food_license, resource2, get_food_license, get_food_license, get_food_license)



        repo.logout()

        return doc

getData.execute()
doc = getData.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

