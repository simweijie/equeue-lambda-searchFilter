import sys
import logging
import pymysql
import json
import os
from pymysql import NULL

#rds settings
rds_endpoint = os.environ['rds_endpoint']
username=os.environ['username']
password=os.environ['password']
db_name=os.environ['db_name']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Connection
try:
    connection = pymysql.connect(host=rds_endpoint, user=username,
        passwd=password, db=db_name)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()
logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def handler(event, context):
    cur = connection.cursor()  
## Retrieve Data
    # note hardcode +8hr due to USA time
    print("inputs:")
    print("clinicId: " + event['clinicId'] + "   district: " + event['district'])
    query = "SELECT b.*,op.opens,op.closes, count(q.id) \
        FROM Branch b, Clinic c, OpeningHours op, Queue q \
        WHERE b.clinicId=c.id AND b.id=op.branchId AND b.id=q.branchId \
        AND c.id='{}' AND b.district='{}' AND current_time+ interval 8 hour BETWEEN opens AND closes \
        AND op.dayOfWeek=dayofweek(now())".format(event['clinicId'],event['district'])    
    cur.execute(query)
    connection.commit()
## Construct body of the response object
    
    branchQueue = []
    rows = cur.fetchall()
    empty = False
    for row in rows:
        print("TEST {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}".format(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))
        if(row[0] == None):
            empty = True;
        else:
            transactionResponse = {}
            transactionResponse['branchId'] = row[0]
            transactionResponse['branchName'] = row[1]
            transactionResponse['district'] = row[2]
            transactionResponse['addr'] = row[3]
            transactionResponse['postal'] = row[4]
            transactionResponse['contactNo'] = row[5]
            transactionResponse['latt'] = row[6]
            transactionResponse['longt'] = row[7]
            transactionResponse['clinicId'] = row[8]
            transactionResponse['opens'] = str(row[9])
            transactionResponse['closes'] = str(row[10])
            transactionResponse['queueLength'] = row[11]
            branchQueue.append(transactionResponse)

# Construct http response object
    responseObject = {}
    if(empty):
        responseObject['data']= {'error':'No clinic available'}
    else:
        responseObject['data']= branchQueue
    return responseObject