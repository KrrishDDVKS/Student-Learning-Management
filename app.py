import streamlit as st
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    database="taskmanage",
    password='KrrishDDVK$7'
)
mycursor=mydb.cursor()
print("Connection Established")

# Establish a connection to MySQL Server
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""

def logout():
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""
    st.session_state["rerun"] = True
    st.rerun()

def login():
    st.title("Login Page")
    userid = st.text_input("email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
            sql= "select password from Users where email= %s"
            val=(userid,)
            mycursor.execute(sql,val)
            pro = mycursor.fetchone()
            if pro is not None: 
                if pro[0] == password:
                    st.session_state["logged_in"] = True
                    sql= "select user_id from Users where email= %s"
                    val=(userid,)
                    mycursor.execute(sql,val)
                    pro = mycursor.fetchone()
                    st.session_state["userid"] = pro[0]

                    sql= "select ManagerID  from Users"
                    mycursor.execute(sql)
                    ro = mycursor.fetchall()
                    unique = sorted(set(x[0] for x in ro))
                    if st.session_state["userid"] in unique:
                        st.session_state["role"] = 'Manager'
                    else:
                        st.session_state["role"] = 'Employ'
                    st.session_state["rerun"] = True
                    st.rerun()  # Refresh to show navigation
                else:
                    st.error("Invalid Password")
            else:
                    st.error("Invalid Userid")


# Create Streamlit App

def mainm():
    st.title("Task Tracker System")

    # Display Options for CRUD Operations
    option=st.sidebar.selectbox("Select an Operation",("Create","Update","Delete","Status"))
    # Perform Selected CRUD Operations
    if option=="Create":
        st.subheader("Create a Task")
        name=st.text_input("Task Name")
        descr=st.text_area("Description")
        dd = st.date_input("DueDate")
        sql= "select status_name  from Task_Status"
        mycursor.execute(sql)
        ro = mycursor.fetchall()
        unique = sorted(set(x[0] for x in ro))
        stat=st.selectbox("Status",unique)
        sql= "select priority_name  from Task_Priority"
        mycursor.execute(sql)
        ro = mycursor.fetchall()
        unique = sorted(set(x[0] for x in ro))
        pri=st.selectbox("Priority",unique)
        sql= "select project_name  from Projects"
        mycursor.execute(sql)
        ro = mycursor.fetchall()
        unique = sorted(set(x[0] for x in ro))
        pro=st.selectbox("Projectname",unique)
        sql= "select team_name  from Teams"
        mycursor.execute(sql)
        ro = mycursor.fetchall()
        unique = sorted(set(x[0] for x in ro))
        team=st.selectbox("Teamname",unique)
        if team==unique[0]:
            a=st.selectbox("Assigned to",("B.Ram","R.Ram","Krishna"))
        
        if team==unique[2]:
            
            a=st.selectbox("Assigned to",("anusha","Ballu","chandra","fatima"))
        if team==unique[4]:
            
            a=st.selectbox("Assigned to",("Krishn","Krish","Kris","Devara"))
        if team==unique[3]:
            
            a=st.selectbox("Assigned to",("eswara","Arjun","Karan","Bheem"))
        if team==unique[1]:
            a=st.selectbox("Assigned to",("Lax","Rama","Laxman","Ra1"))
        if st.button("Create"):
            sql="select project_id from projects where project_name= %s"
            val=(pro,)
            mycursor.execute(sql,val)
            pro = mycursor.fetchall()

                
            sql="select status_id from Task_Status where status_name= %s"
            val=(stat,)
            mycursor.execute(sql,val)
            stat = mycursor.fetchall()
            
            
            sql="select priority_id from task_priority where priority_name= %s"
            val=(pri,)
            mycursor.execute(sql,val)
            pri = mycursor.fetchall()
            print(pri)

            sql= "insert into Tasks(task_title,description,duedate,status_id,priority_id,project_id) values(%s,%s,%s,%s,%s,%s)"
            val= (name,descr,dd,stat[0][0],pri[0][0],pro[0][0])
            mycursor.execute(sql,val)
            mydb.commit()
            

            sql="select user_id from Users where name= %s"
            val=(a,)
            mycursor.execute(sql,val)
            a = mycursor.fetchall()
            print(a)

            sql="select CURDATE()"
            mycursor.execute(sql)
            d = mycursor.fetchall()
            print(d)

            sql="select task_id from Tasks ORDER BY task_id DESC LIMIT 1;"
            mycursor.execute(sql)
            i = mycursor.fetchall()
            print(i)

            sql="insert into Task_Assignees(task_id,user_id,assignment_date) values(%s,%s,%s)"
            val= (i[0][0],a[0][0],d[0][0])
            mycursor.execute(sql,val)
            mydb.commit()
            st.success("Task Created Successfully!!!")

    elif option=="Status":
        st.subheader("Task Status")
        sql='select t.task_id, t.task_title, t.description, t.duedate, ts.status_name, tp.priority_name, p.project_name,tea.team_name, u.name, u.email, c.user_id,c.created_at, c.comment_text from Tasks t left join Comments c on c.task_id=t.task_id join Task_Status ts on t.status_id=ts.status_id join Task_Priority tp on t.priority_id=tp.priority_id join Projects p on t.project_id=p.project_id join Team_Projects tep on t.project_id=tep.project_id join Teams tea on tep.team_id=tea.team_id join Task_Assignees ta on t.task_id=ta.task_id join Users u on ta.user_id=u.user_id'
        val=(st.session_state['userid'])
        mycursor.execute(sql,val)
        result = mycursor.fetchall()
        for row in result:
            arow={'ID':row[0],'Title':row[1],'Description':row[2],'Due Date':row[3],'Status':row[4],'priority':row[5],'project':row[6],'Team':row[7],'Assigned To':row[8],'Email':row[9],'comments':{'id':row[10],'time':row[11],'text':row[12]}}
            st.write(arow)

    elif option=="Update":
        st.subheader("Update a Task")
        id=st.text_input("ID")
        name=st.text_input("Task new Name")
        descr=st.text_input("new Description")
        dd = st.date_input("new DueDate")
        stat=st.selectbox("new Status",("Pending","Inprogress","Completed"))
        pri=st.selectbox("new Priority",("High","Medium","Low"))
        pro=st.selectbox("new Projectname",("TML","FCA"))
        sql="select project_id from projects where project_name= %s"
        val1=(pro,)
        mycursor.execute(sql,val1)
        pro = mycursor.fetchall()
        sql="select status_id from Task_Status where status_name= %s"
        val2=(stat,)
        #print(val2)
        mycursor.execute(sql,val2)
        stat = mycursor.fetchall()
        #print(stat)
        sql="select priority_id from task_priority where priority_name= %s"
        val3=(pri,)
        #print(val3)
        mycursor.execute(sql,val3)
        pri = mycursor.fetchall()
        print(pri)
        if st.button("Update"):
            sql="update Tasks set task_title=%s,description=%s,duedate=%s,status_id=%s,priority_id=%s,project_id=%s where task_id =%s"
            val= (name,descr,dd,stat[0][0],pri[0][0],pro[0][0],id)
            print(val)
            mycursor.execute(sql,val)
            mydb.commit()
            st.success("Task Updated Successfully!!!")




    elif option=="Delete":
        st.subheader("Delete a Task")
        id=st.number_input("Task ID",min_value=1)
        if st.button("Delete"):
            sql="delete from Task_Assignees where task_id =%s"
            val=(id,)
            mycursor.execute(sql,val)
            mydb.commit()
           
            sql="delete from Tasks where task_id =%s"
            val=(id,)
            mycursor.execute(sql,val)
            mydb.commit()
            
            st.success("Task Deleted Successfully!!!")

    if st.button("Logout"):
        logout()


def maine():
    st.title("Task Tracker System")

    # Display Options for CRUD Operations
    option=st.sidebar.selectbox("Select an Operation",("Update","Status"))
    # Perform Selected CRUD Operations
    
    if option=="Status":
        st.subheader("Task Status")
        sql='select t.task_id, t.task_title, t.description, t.duedate, ts.status_name, tp.priority_name, p.project_name,tea.team_name, u.name, u.email, c.user_id,c.created_at, c.comment_text from Tasks t left join Comments c on c.task_id=t.task_id join Task_Status ts on t.status_id=ts.status_id join Task_Priority tp on t.priority_id=tp.priority_id join Projects p on t.project_id=p.project_id join Team_Projects tep on t.project_id=tep.project_id join Teams tea on tep.team_id=tea.team_id join Task_Assignees ta on t.task_id=ta.task_id join Users u on ta.user_id=u.user_id where u.user_id=%s;'
        val=(st.session_state['userid'],)
        mycursor.execute(sql,val)
        result = mycursor.fetchall()
        for row in result:
            arow={'ID':row[0],'Title':row[1],'Description':row[2],'Due Date':row[3],'Status':row[4],'priority':row[5],'project':row[6],'Team':row[7],'Assigned To':row[8],'Email':row[9],'comments':{'id':row[10],'time':row[11],'text':row[12]}}
            st.write(arow)
            



    elif option=="Update":
        st.subheader("Update a Task")
        sql='select task_id from Task_Assignees where user_id=%s'
        val=(st.session_state['userid'],)
        mycursor.execute(sql,val)
        result = mycursor.fetchall()
        print(result)
        print('result')
        flat_list = [x[0] for x in result]
        
        id=st.selectbox("Task ID",flat_list)
        stat=st.selectbox("new Status",("Pending","Inprogress","Completed"))
        com=st.text_area("Comment")
        sql='select status_id from Task_Status where status_name=%s'
        val2=(stat,)
        print('stat')
        print(stat)
        mycursor.execute(sql,val2)
        stat = mycursor.fetchall()
        
        if st.button("Update"):
            sql="update Tasks set status_id=%s where task_id =%s"
            val= (stat[0][0],id)
            print(val)
            mycursor.execute(sql,val)
            mydb.commit()
            
            sql="SELECT CURRENT_TIMESTAMP();"
            mycursor.execute(sql)
            d = mycursor.fetchall()
            print(d)
            sql="insert into Comments(task_id,user_id,Created_at,comment_text) values(%s,%s,%s,%s)"
            val= (id,st.session_state['userid'],d[0][0],com)
            mycursor.execute(sql,val)
            mydb.commit()
            st.success("Task Updated Successfully!!!")
            #if

    if st.button("Logout"):
        logout()



if __name__ == "__main__":
    if not st.session_state["logged_in"]:
        login()
    else:
        if st.session_state['role']=='Manager':
            mainm()
        else:
            maine()
