# BrandPulseAI
This project is conducted by a group of 4th-year SLIIT Students on behalf of their Final Year Research. 


# Clone the project

1. Go to the place you want to create the project folder (In your Local Machine), Then right click and open 'git bash here'. 
(If u don't have Git Bash, download it)
2. Now type -> git clone -b main https://github.com/IT21468360/BrandPulseAI.git
3. Then a folder will be created with the name 'BrandPulseAI'
4. Open it in the VS code

# Set up the environement

1. Create .env files.
1.1 -> Inside 'frontend-backend-nextjs' folder. 
       Create file '.env.local'
       Then type the below:
       
MONGODB_URI=mongodb+srv://Admin:research_autn@cluster0.mongodb.net/brandpulse?retryWrites=true&w=majority
JWT_SECRET=your_jwt_secret_key
PORT=3000

1.2 -> Inside 'backend-python' folder. 
       Create file '.env'
       Then type the below:
       
MONGODB_URI=mongodb+srv://Admin:research_autn@cluster0.mongodb.net/brandpulse?retryWrites=true&w=majority

2. Setting up the Environment

2.1. Set up virtual environment
  1)  ctrl+shift+p
  2) select python: select interpreter
  3) Create virtual environment
  4) .conda -> python 3.12.8
 
2.2. Setting up Python Backend
Terminal -> Git Bash -> Execute the below commands
1) cd backend-python
2) pip install -r requirements.txt
3) (After installed successfully)
uvicorn app.main:app --reload --port 8000    -> Command to run the python backend
4) It will show as 'Application startup complete'.
5) http://127.0.0.1:8000/  go to this an check whether it is working.

2.3. Setting up Next.js
Terminal -> Git Bash -> Execute the below commands
1) cd frontend-backend-nextjs
2) npm install (Yoou might get version errors, fix them using chat gpt)
3) npm run dev    -> Command to run the next.js backend and frontend
4) It will show as 'Ready in ...'.
5) http://localhost:3000  go to this an check whether it is working.

# Setting up MongoDB compass 
1. Download MongoDB compass if u don't have it.
2. open it.
3. Enter below url
mongodb+srv://Admin:research_autn@cluster0.lihl5.mongodb.net/

# Where to do your work

1. Under Notebook section, each of u have folders. U can create ur notebooks there. Save ur models inside the folder for now. 
2. In the Data section u can upload ur CSVs, RAW and pre-processed both.

# Creating Branches, Push , Pull

 -> All the commands shoud be executed in Git Bash Terminal
 
1. I have created Branches for each of u. If u need any other branches, u can create them manually in GitHub (Branch source should be "main")
2. Make sure to 'pull' others work to ur local-repo, before u start working everytime.
3. 'git pull' command. (Make sure to run this command before pushing your modifications)
   
4. After doing ur modifications,
In the terminal do the following (Make sure you are using git bash terminal)

#Changes will be commited to the local repo 
1. git add . (This command is used to add all the changes you made) (If you want to add only specific files or folders, You can give its name. ex: git add filename.extension ) 
2. git commit -m "type message what you changed"

#Push to your branch in the remote repo 
3. git push origin main:my-branch    
Ex: git push origin main:sentiment_analysis

After pushing changes to ur branch, u hv to merge ur chages to the main branch.
You can do it ur self or u can drop a msg to me.
When merging make sure u don't hv any conflicts. If u have any then make sure to resolve them.





