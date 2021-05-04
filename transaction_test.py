# imports for transaction
import pymysql as mysql
from datetime import date

# imports for testing
from multiprocessing import Process
import time

db = mysql.connect(host="localhost",user="root",
                   password="password", database="Enterprise",autocommit=False)

# run same transaction at the same time to check for concurrency
def test_transaction(count):
    p1 = Process(target=transaction,args=(1,))
    p2 = Process(target=transaction,args=(2,))
    p1.start()
    p2.start()

# just uses model_id=1 and account Colton Willhardt
def transaction(thread=1):
    
    print(str(thread)+' '+str(time.ctime(time.time())))
    name = "Colton Willhardt"
    print("name: "+name)
    try:
        db.begin()
        cursor = db.cursor()
            
        # make sure items in stock, else raise exception and rollback
        sql = "SELECT count FROM stock WHERE store_id=1 AND model_id=1 FOR UPDATE"
        cursor.execute(sql)
        count = cursor.fetchone()[0]
        print("count: "+str(count))
        if count < 1:
            raise Exception('Model out of stock. Purchase failed')
        else:
            sql = "UPDATE stock SET count = count-1 WHERE store_id=1 AND model_id=1"
            cursor.execute(sql)
                    
        # get the apple_id
        sql = "SELECT apple_id FROM apple_account WHERE name='"+name+"'"
        cursor.execute(sql)
        account_id = cursor.fetchone()[0]
        print(account_id)
  
        # insert into checkout and get checkout_id
        today = date.today()
        today = today.strftime('%Y-%m-%d %H')
        sql = "INSERT INTO checkout(date,payment_method,store_id,apple_id) "\
                "VALUES ('"+today+"','Bitcoin',1,"+str(account_id)+")"
        cursor.execute(sql)
        cursor.execute("SELECT last_insert_id()")
        checkout_id = cursor.fetchone()[0]
        print(checkout_id)
        
        # insert model 1 into product_purchases
        sql = "SELECT price FROM stock WHERE store_id=1 AND model_id=1"
        cursor.execute(sql)
        cost = cursor.fetchone()[0]
        sql = "INSERT INTO product_purchases(model_id,checkout_id,cost)"\
            " VALUES("+"1"+","+str(checkout_id)+","+str(cost)+")"
        cursor.execute(sql)
                
        db.commit()
        print("success")

    except:
        try:
            db.rollback()
            print("rollback")
        except:
            print("rollback failed")

if __name__=="__main__":
    test_transaction(3)


    
