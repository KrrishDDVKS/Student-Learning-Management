import streamlit as st
from pymongo import MongoClient
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
from pymongo import MongoClient
import gridfs
import base64
import io
from datetime import datetime, time

# Simulated user database
client = MongoClient('mongodb+srv://krrish852456:krrish852456@cluster0.99khz.mongodb.net/?retryWrites=true&w=majority&appid=Cluster0')

db = client["slms"]
dba=client['assign']
collection = db["slms"]
collection1 = db["Subjects"]
collection2 = db["Instructor"]
cust = db["Customer Care"]
assign=db["assign"]
m=db["modules"]
p=db["payment"]
fs = gridfs.GridFS(db)
fsa = gridfs.GridFS(dba)
# Session state initialization
if "reg_in" not in st.session_state:
    st.session_state["reg_in"] = False
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""


#Logout Function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""
    st.session_state["rerun"] = True
    st.rerun()


#Reg function
def reg(x):
    new_userid = st.text_input("New Userid")
    new_password = st.text_input("New Password", type="password")
    s=st.text_input("Specialization")
    'Already have an Account'
    if st.button('Login Page'):
        st.session_state["reg_in"] = False
        st.session_state["rerun"] = True
        st.rerun()
        
    if st.button("Register"):
        if collection.find_one({"id": new_userid}) is not None:
            st.warning("The UserID already EXIST.")
        else:
            if new_userid and new_password:
                y={"id":new_userid,"pwd":new_password,"role":x,"spec":s,"bal":300}
                collection.insert_one(y)
                st.session_state["reg_in"] = False
                st.session_state["rerun"] = True
                st.rerun()
            else:
                st.warning("Please enter both userid and password.")

def display_pdf(pdf_bytes):
    st.warning("Please don't upload PDF file. The PDF file viwer is not working on Cloud")
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def retrival(c,i,o):
    module=[]
    pdf_files = list(db.fs.files.find({}, {"metadata": 1}))
    if pdf_files!=[]:
        for file in pdf_files:
            metadata = file.get("metadata", {})
            print(metadata)
            if metadata['course']==c and metadata['id']==i and metadata['option']==o:
                module.append(metadata['name'])
    n=m.find({'id':i,'option':o},{"name":1})
    if n is not None:
        for f in n:
            module.append(f['name'])
        selected_filename = st.selectbox("Select a PDF to View",module)

    query = {"metadata.name": selected_filename}
    results = list(db.fs.files.find(query, {"metadata": 1}))
    print('results')
    print(results)
    if results !=[]:
        st.write(results[0]['metadata']['description'])
        file_id = results[0]['_id']
        print('p')
        print(file_id)
        pdf_data = fs.get(file_id).read()
        if results[0]['metadata']['filename'].split(".")[1]=='pdf':
            display_pdf(pdf_data)
        st.download_button(label="Download PDF", data=pdf_data, file_name=selected_filename)    
    

    n=m.find_one({"name":selected_filename})
    if n is not None:
        st.write(n['description'])
    return(selected_filename)

def retrivala(c,i):
    module=[]
    pdf_files = list(db.fs.files.find({}, {"metadata": 1}))
    if pdf_files!=[]:
        for file in pdf_files:
            metadata = file.get("metadata", {})
            if metadata['course']==c and metadata['id']==i and metadata['option']==o:
                module.append(metadata['name'])
    
    n=m.find({'id':i,'option':o},{"name":1})
    
    if n is not None:
        for f in n:
            module.append(f['name'])
        selected_filename = st.selectbox("Select a PDF to View",module)

    query = {"metadata.name": selected_filename}
    results = list(db.fs.files.find(query, {"metadata": 1}))
    if results!=[]:
        st.write(results[0]['metadata']['description'])
        # Dropdown to select a PDF file
        # Retrieve the PDF file from MongoDB
        file_id = results[0]['_id']
        pdf_data = fs.get(file_id).read()
        if results[0]['filename'].split(".")[1]=='pdf':
            display_pdf(pdf_data)
        # Convert to bytes and display
        st.download_button(label="Download PDF", data=pdf_data, file_name=selected_filename)
        print('r')
        print(results)
        if results[0]['metadata']['option']=='Assignment':
            return((results[0]['metadata']['dead'],selected_filename))
        
    n=m.find_one({"name":selected_filename})
    if n is not None:
        st.write(n['description'])
        if n['option']=='Assesment':
            return(n['dead'],selected_filename)

# Login function
def login():
    st.title("Login Page")
    userid = st.text_input("Userid")
    password = st.text_input("Password", type="password")
    'Create an Account'
    if st.button('Registration form'):
        st.session_state["reg_in"] = True
        st.experimental_rerun()
    if st.button("Login"):
            user = collection.find_one({"id": userid})
            if user is not None: 
                if user["pwd"] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["userid"] = userid
                    st.session_state["role"] = user["role"]
                    st.session_state["rerun"] = True
                    st.rerun()  # Refresh to show navigation
                else:
                    st.error("Invalid Password")
            else:
                    st.error("Invalid Userid")

def moduleview():
    st.title("📄 Retrieve and Display PDFs from MongoDB")

    # Fetch all stored PDF files
    pdf_files = list(db.fs.files.find({}, {"filename": 1, "_id": 1}))

    # Dropdown to select a PDF file
    if pdf_files!=[]:
        file_options = {file["filename"]: file["_id"] for file in pdf_files}
        selected_filename = st.selectbox("Select a PDF to View", list(file_options.keys()))

        if st.button("Load PDF"):
            # Retrieve the PDF file from MongoDB
            file_id = file_options[selected_filename]
            pdf_data = fs.get(file_id).read()
            
            # Convert to bytes and display
            st.download_button(label="Download PDF", data=pdf_data, file_name=selected_filename, mime="application/pdf")
            
            st.write("📄 **PDF Preview:**")
            st.pdf(io.BytesIO(pdf_data))
    else:
        st.write("⚠️ No PDFs found in the database.")

def mainc():
    st.session_state.notif=[]
    llm=ChatOpenAI(api_key=st.secrets["OPEN_API_KEY"],                            #st.secrets["OPEN_API_KEY"]
                   model_name='gpt-4o',
                   temperature=0.0)
    prompt_template='''If any actionable prompt is given the state yes else give the response.   
    Text:
    {context}'''
    PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context"])
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hello! Welcome to customer care. How Can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
    
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        chain = LLMChain(llm=llm, prompt=PROMPT)
        answer=chain.run(prompt)
        if re.search(r'\bYes\b', answer):
            cust.insert_one({'id':st.session_state["userid"],'query':prompt})
            st.chat_message("assistant").write("Notified to the Admin, He will get back to you soon...")
        else:
            prompt_template='''Accept the queries as a customer care and give an accuarte reply.   
            Text:
            {context}'''
            PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context"])
            chain = LLMChain(llm=llm, prompt=PROMPT).run(prompt)
            st.session_state.messages.append({"role": "assistant", "content": chain})
            st.chat_message("assistant").write(chain)
       
# Main app interface Student
def maini():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Module", "view Assignments","Payment","Customer Care"])

    if page == "Dashboard":
        st.title("Dashboard")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        documents=collection2.find({"Instructor": {"$in": [st.session_state["userid"]]}},{"course": 1, "_id": 0})
        key_values = [doc['course'] for doc in documents if 'course' in doc]
        optionm = st.selectbox("Course",(key_values))

    elif page == "Module":
        st.title("Module")
        st.write("Welcome to the Module creation page.")
        flag = st.toggle("AI Correction")
        documents=collection2.find({"Instructor": {"$in": [st.session_state["userid"]]}},{"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        optionm = st.selectbox("Course",(key_values))
        name=st.text_input("Enter the module name")
        e=1
        existing_file = db.fs.files.find_one({"metadata.name": name})
        e=m.find_one({"name":name})
        if existing_file is not None or e is not None:
            st.warning("⚠️ A file with this unique ID already exists! Please enter a different ID.")
        else:
            description=st.text_area("Enter the text")
            # File uploader widget
            uploaded_file = st.file_uploader("Upload a PDF file", type=[])
            option = st.selectbox("Module",('Learning Content','Assignment','Assesment'))
            if option=='Learning Content' or option=='Assignment':
                if option=='Assignment':
                    'Enter Assignment Deadline'
                    d=st.date_input("📅Date:",format='MM/DD/YYYY')
                    t=st.time_input("⏰Time:",value=time(0,0))
                    dt= datetime.combine(d,t)
                if st.button("Upload"):
                    if uploaded_file.name.split('.')[1]=='pdf':
                        st.warning("Please don't upload PDF file. The PDF file viwer is not working on Cloud.")
                    else:
                        if uploaded_file is not None:
                            st.success(f"✅ Uploaded: {uploaded_file.name}")
    
                            # Convert file to binary for MongoDB storage
                            file_data = uploaded_file.read()
                            
                            # Check if file already exists in MongoDB
                            existing_file = db.fs.files.find_one({"filename": uploaded_file.name})
                            
                            if existing_file:
                                st.warning("⚠️ File already exists in MongoDB.")
                            else:
                                # Store file in GridFS
                                if option=='Learning Content':
                                    file_id = fs.put(file_data, filename=uploaded_file.name,metadata={"filename":uploaded_file.name,"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option})
                                    st.success(f"📁 File saved to MongoDB with ID: {file_id}")
                                else:
                                    file_id = fs.put(file_data, filename=uploaded_file.name,metadata={"filename":uploaded_file.name,"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'dead':dt})
                                    st.success(f"📁 File saved to MongoDB with ID: {file_id}")
                    
                        else:
                            if option=='Learning Content':
                                m.insert_one({"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option})
                                st.success(f"✅ Uploaded")
                            else:
                                m.insert_one({"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'dead':dt})
                                st.success(f"✅ Uploaded")

            if option=='Assesment':
                choice = st.selectbox("Type of Question",('Descriptive','MCQ','More than One Answer MCQ','True or False'))
                if choice=='Descriptive':
                    if st.button("Upload"):
                        if uploaded_file is not None:
                            st.success(f"✅ Uploaded: {uploaded_file.name}")

                            # Convert file to binary for MongoDB storage
                            file_data = uploaded_file.read()
                            
                            # Check if file already exists in MongoDB
                            existing_file = db.fs.files.find_one({"filename": uploaded_file.name})
                            
                            if existing_file:
                                st.warning("⚠️ File already exists in MongoDB.")
                            else:
                                # Store file in GridFS
                                file_id = fs.put(file_data, filename=uploaded_file.name,metadata={"filename":uploaded_file.name,"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice})
                                st.success(f"📁 File saved to MongoDB with ID: {file_id}")

                        else:
                            m.insert_one({"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice})
                            st.success(f"✅ Uploaded")

                if choice=='MCQ' or choice=='More than One Answer MCQ':
                    n=int(st.text_input("No. of options:",4))
                    a=[]
                    for i in range(n):
                        x=st.text_input(f"{i}.")
                        a.append([x])
                    if st.button("Upload"):
                            if uploaded_file is not None:
                                st.success(f"✅ Uploaded: {uploaded_file.name}")

                                # Convert file to binary for MongoDB storage
                                file_data = uploaded_file.read()
                                
                                # Check if file already exists in MongoDB
                                existing_file = db.fs.files.find_one({"filename": uploaded_file.name})
                                
                                if existing_file:
                                    st.warning("⚠️ File already exists in MongoDB.")
                                else:
                                    # Store file in GridFS
                                    file_id = fs.put(file_data, filename=uploaded_file.name,metadata={"filename":uploaded_file.name,"name": name, "course": option, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice,'a':a})
                                    st.success(f"📁 File saved to MongoDB with ID: {file_id}")

                            else:
                                m.insert_one({"name": name, "course": option, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice,'a':a})
                                st.success(f"✅ Uploaded")
        
                if choice=='True or False':
                    if st.button("Upload"):
                            if uploaded_file is not None:
                                st.success(f"✅ Uploaded: {uploaded_file.name}")

                                # Convert file to binary for MongoDB storage
                                file_data = uploaded_file.read()
                                
                                # Check if file already exists in MongoDB
                                existing_file = db.fs.files.find_one({"filename": uploaded_file.name})
                                
                                if existing_file:
                                    st.warning("⚠️ File already exists in MongoDB.")
                                else:
                                    # Store file in GridFS
                                    file_id = fs.put(file_data, filename=uploaded_file.name,metadata={"filename":uploaded_file.name,"name": name, "course": option, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice})
                                    st.success(f"📁 File saved to MongoDB with ID: {file_id}")

                            else:
                                m.insert_one({"name": name, "course": option, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice})
                                st.success(f"✅ Uploaded")
    
    elif page == "view Assignments":
        st.title("view Assignments")
        module=[]
        documents=collection2.find({"Instructor": {"$in": [st.session_state["userid"]]}},{"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
            optionm = st.selectbox("Course",(key_values))

        pdf_files = list(db.fs.files.find({}, {"metadata": 1}))
        if pdf_files!=[]:
            for file in pdf_files:
                metadata = file.get("metadata", {})
                if metadata['course']==optionm:
                    module.append(metadata['name'])
        n=m.find({},{"name":1})
        if n is not None:
            for f in n:
                module.append(f['name'])
        selected_filename = st.selectbox("Select module",module)
        pdf_files = dba.fs.files.find({'filename': {"$regex": selected_filename}}, {"filename": 1})
        print('pdf_files')
        print(pdf_files)
        a=[]
        if pdf_files is not None:
            for i in pdf_files:
                print(i)
                a.append(i['filename'])    
        selected_filename = st.selectbox("Select a PDF to View",a)
        file_id = dba.fs.files.find_one({"filename":selected_filename}, {"_id": 1})
        print('id')
        print(file_id)
        if file_id is not None:
            pdf_data = fsa.get(file_id['_id']).read()
            if 'pdf' in selected_filename.split('.'):
                display_pdf(pdf_data)
        # Convert to bytes and display
        st.download_button(label="Download PDF", data=pdf_data, file_name=selected_filename)

    elif page == "Customer Care":
        st.title("Customer Care")
        mainc()

    if st.button("Logout"):
        logout()

# Main app interface Instructor
def mains():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Module", "Assignment","Assesment","Payment","Customer Care"])

    if page == "Dashboard":
        st.title("Home Page")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        documents = p.find({}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = p.find({"spec":s}, {"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        c = st.selectbox("course",key_values)
        
    elif page == "Module":
        st.title("Admin Dashboard")
        st.write("Welcome to the admin page.")
        documents = p.find({}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = p.find({"spec":s}, {"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        c = st.selectbox("course",key_values)
        ins = p.find_one({"spec":s,'course':c}, {"instructor": 1, "_id": 0})
        if ins is not None:
            i=ins['instructor']
            retrival(c,i,'Learning Content')

    elif page == "Assignment":
        st.title("User Dashboard")
        st.write("Welcome to the user page.")
        documents = p.find({}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = p.find({"spec":s}, {"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        c = st.selectbox("course",key_values)
        ins = p.find_one({"spec":s,'course':c}, {"instructor": 1, "_id": 0})
        if ins is not None:
            i=ins['instructor']
            m=retrival(c,i,page)

        uploaded_file = st.file_uploader("Upload a PDF file", type=[])
        if st.button('upload'):
            if uploaded_file is not None:
                file_data = uploaded_file.read()
                file_id = fsa.put(file_data, filename=f'{m}.{i}.{uploaded_file.name}.{st.session_state["userid"]}',metadata={'upload_time':datetime.utcnow()})
                st.success(f"📁 File saved to MongoDB with ID: {file_id}")

    elif page == "Assesment":
        st.title("Assesment")
        st.write("Welcome to the user page.")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = collection1.find({"spec":s}, {"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
            c = st.selectbox("course",key_values[0])
        ins = p.find_one({"spec":s,'course':c}, {"instructor": 1, "_id": 0})
        if ins is not None:
            i=ins['instructor']
            mod=retrival(c,i,page)
        ans=st.text_area('Enter the Answer')
        assign.insert_one({'mod':mod[1],'ans':ans})

    elif page == "Payment":
        st.title("Payment")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))
        if documents is not None:
            documents = collection1.find({"spec":s}, {"course": 1, "_id": 0})
            key_values = [doc['course'] for doc in documents if 'course' in doc]
            c = st.selectbox("course",key_values[0])

        exist=p.find_one({'course':c})
        if exist is None:
            documents = collection2.find({"spec":s,"course":c}, {"Instructor": 1, "_id": 0})
           
            key_values = [doc['Instructor'] for doc in documents if 'Instructor' in doc]
            
            ins = st.selectbox("Instructor",key_values[0])
            if st.button('pay'):
                b=collection.find_one({'id':st.session_state['userid']},{"bal":1})
                if b['bal']!=0:
                    i=b['bal']-100
                    collection.update_one({"id": st.session_state['userid']}, {"$set":{'bal':i}})
                    p.insert_one({"id":st.session_state['userid'],"spec":s,"course":c,"instructor":ins})
                    st.success(f"payed successfully, you have {i} balance in your account")
                else:
                    st.error("No enough balance")
        else:
            st.warning("Already Payed")

    elif page == "Customer Care":
        st.title("Customer Care")
        mainc() 

    if st.button("Logout"):
        logout()


# Main app interface Admin
def maina():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home Page","Instruct Reg", "Course Reg", "Course View","Course Assign","Assign View","Notification"])
    
    if page == "Home Page":
        st.title("Home Page")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")

    elif page == "Instruct Reg":
        st.title("Instructor Registration")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        reg("Instructor")

    elif page == "Course Reg":
        st.title("Course Registration")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        s=st.text_input("Specialization")
        c=st.text_input("Course")
        exist=collection1.find({'course':c})
        if st.button("Insert"):
                if exist is None:
                    spec=collection1.find_one({"spec": s})
                    if  spec is not None:
                    # Append new values to the existing array
                        a=spec['course']
                        a.append(c)
                        collection1.update_one({"spec": s}, {"$set":{'course':a}})
                        st.success(f"Data appended successfully to key: {c}")
                    else:
                    # Create a new document if key does not exist
                        collection1.insert_one({'spec':s,'course':[c]})
                        st.success(f"New key created, data inserted: {s}")
        else:
            st.warning("The Subject Already Exist")

    elif page == "Course View":
        st.title("Course View")
        st.write("Welcome to the Course View.")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        option = st.selectbox("Specialization",(key_values))
        if option:
        # Find all documents where the key exists
            courses = collection1.find({'spec':option})
            if documents:
                st.write(f"Documents with the key '{option}':")
                st.dataframe(courses)  # Display documents in a table format
            else:
                st.write(f"No documents found with the key: {option}")

    elif page == "Course Assign":
        st.title("Course Registration")
        st.write("Welcome to the Course page.")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = collection1.find({"spec":s}, {"course": 1, "_id": 0})
        key_values = [doc['course'] for doc in documents if 'course' in doc]
        c = st.selectbox("course",key_values[0])

        docum = collection.find({"role":"Instructor","spec":s}, {"id": 1, "_id": 0})
        key_values = [doc['id'] for doc in docum if 'id' in doc]
        i = st.selectbox("Instructor",(key_values))

        if st.button("Insert"):
            spec=collection2.find_one({"spec": s,'course':c})
            if  spec is not None:
                # Append new values to the existing array
                a=spec['Instructor']
                a.append(i)
                collection2.update_one({"spec": s,'course':c}, {"$set":{'Instructor':a}})
                st.success(f"Data appended successfully to key: {c}")
            else:
                # Create a new document if key does not exist
                collection2.insert_one({'spec':s,'course':c,'Instructor':[i]})
                st.success(f"New key created, data inserted: {s}")

    elif page == "Assign View":
        st.title("Assign View")
        st.write("Welcome to the Assign View.")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        option = st.selectbox("Specialization",(key_values))
        if option:
        # Find all documents where the key exists
            courses = collection2.find({'spec':option})
            if documents:
                st.write(f"Documents with the key '{option}':")
                st.dataframe(courses)  # Display documents in a table format
            else:
                st.write(f"No documents found with the key: {option}")

    elif page == "Notification":
        st.title("Customer Service")
        if "messages" not in st.session_state:
            st.write("No Notifications")
        else:
            st.write(st.session_state.messages)

    if st.button("Logout"):
        logout()


# Control access
if not st.session_state["reg_in"]:
    if not st.session_state["logged_in"]:
        login()
    else:
        if st.session_state['role']=='Student':
            mains()
        if st.session_state['role']=='Admin':
            maina()
        if st.session_state['role']=='Instructor':
            maini()

else:
    reg("Student")
