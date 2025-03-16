# BrandPulseAI - research
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
       
MONGODB_URI=mongodb+srv://it21468360:it21468360@researchcluster.vctn1.mongodb.net/BrandPulseAI?retryWrites=true&w=majority
DB_NAME=BrandPulseAI
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRY=86400
PORT=3000
NODE_OPTIONS="--dns-result-order=ipv4first"


1.2 -> Inside 'backend-python' folder. 
       Create file '.env'
       Then type the below:
       
MONGODB_URI=mongodb+srv://it21468360:it21468360@researchcluster.vctn1.mongodb.net/BrandPulseAI?retryWrites=true&w=majority
DB_NAME=BrandPulseAI
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRY=86400
PORT=3000

2. Setting up the Environment

2.1. Create a virtual environment : ( I have povide examples below. You can use the names you want)
In the Terminal Power Shell), Type below commands.
  1) To Create ->  conda create --name brandpulse python=3.10 -y (For pyython use this version)
  2) Activate your environment -> conda activate brandpulse
  3) To check available Environments -> conda env list

 
Install the requirements:
1. If Python or pip is not installed inside the environment, Install them using the commands. (get them from chatgpt)
2. Terminal -> Power shell -> Execute the below commands
3. Then run -> pip install nltk
4. next ->
pip install --no-cache-dir -r requirements.txt
 (if this didn't work, use the below command)
python -m pip install -r requirements.txt
5. Then run -> python -m spacy download en_core_web_sm
6. Check whether it succeded wiithout any errors. 


2.2. Setting up Python Backend
Terminal  -> Execute the below commands
1) cd backend-python
2) uvicorn app.main:app --reload --port 8000    -> Command to run the python backend
3) It will show as 'Application startup complete'.
4) http://127.0.0.1:8000/  go to this an check whether it is working.

2.3. Setting up Next.js
Terminal -> Execute the below commands
1) cd frontend-backend-nextjs
2) npm install (Yoou might get version errors, fix them using chat gpt)
3) npm run dev    -> Command to run the next.js backend and frontend
4) It will show as 'Ready in ...'.
5) http://localhost:3000  go to this an check whether it is working.

# Setting up MongoDB compass 
1. Download MongoDB compass if u don't have it.
2. open it.
3. Add new Connection
4. Enter below url
mongodb+srv://it21468360:it21468360@researchcluster.vctn1.mongodb.net/BrandPulseAI?retryWrites=true&w=majority


# Where to do your work

1. Under Notebook section, each of u have folders. U can create ur notebooks there. Save ur models inside the folder for now. 
2. In the Data section u can upload ur CSVs, RAW and pre-processed both.

# Creating Branches, Push , Pull

 -> All the commands shoud be executed in Git Bash Terminal.
 Also make sure, u r always in the right path, before executing any command.
 
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

# New Requirements and dependencies

1. If u need any requirement or dependency which is not mentoioned already.
(Like Python Libraries or anything)
Make sure to install them, and also update the requirement.txt file (Make sure they are compatible with other python library versions.)
