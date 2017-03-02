# coding: utf-8 
from dbconnect import connection

cur, conn = connection()
repeated_list = []

def get_repeated_url_to_list():
    count=0
    with open("urls.seen") as f:  # Get unrepeated distinct urls from SQL commands
        for index,url in enumerate(f):
            url=url[:-1]  # the last character is '\n'
            cur.execute("SELECT * FROM `shops` WHERE url='%s'"%url)
            a=cur.fetchall()
            if len(a)>1:
                print("repeated one----")
                repeated_list.append(url)
            else:
                count=count+1
                print(count)

def delete_repeated_records_inDB():
    for index,url in enumerate(repeated_list):
        #if index<10: 
        cur.execute("SELECT * FROM `shops` WHERE url='%s'"%url)
        a = cur.fetchall()
        success_index =a.index(sorted(a,key=tuple_to_string,reverse=True)[0])
        failed_index  = [i for i in range(len(a)) if i!=success_index]
        failed_shop_id = [a[j][0] for j in failed_index]
        #print("url:{},failed_shop_id:{}".format(url,failed_shop_id))
        # delete
        for id in failed_shop_id:
            cur.execute("DELETE FROM `shops` WHERE url='%s' and id='%s'"%(url,id))
            conn.commit()
            print(index)


def tuple_to_string(t):
    """"""
    ls = list(t)
    ls = [str(i) for i in ls]
    return len("".join(ls))



if __name__ == '__main__':
    get_repeated_url_to_list()
    delete_repeated_records_inDB()