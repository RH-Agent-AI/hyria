import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_tool_calling_agent
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.tools import tool
from langchain.agents import AgentExecutor
from IPython.display import display, Markdown
import json
import requests
os.environ["MISTRAL_API_KEY"] = "OZSyUAoFi2DmsjJz5Cuqg8vWeFzG9grq"


def extract_from_cv(file_path: str) -> str:
    """Extract information from CV
    """
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    return pages[0].page_content

def create_candidat(candidat):
    """create candidats from phone number
    args:
        candidat: dict: candidat to create can contains one or more of the following keys: {"first_name": "string", "last_name": "string", "address": "string", "email": "string", "phone": "string",  "cv_text": "string mandatory "}
    """
    response = requests.post(f"https://hr-api-endpoints.onrender.com/candidats", json=candidat)
    return str(response.status_code) + response.text
@tool
def get_candidat(phone):
    """create candidats from phone number
    args:
        phone: str: candidat phone number that should like +33xxxxxxxxx without 0 or (0) after the +33 and without any space.
        """
    response = requests.get(f"https://hr-api-endpoints.onrender.com/candidats?phone="+phone)
    return str(response.status_code) + response.text
@tool
def get_applications(id, content):
    """create candidats from phone number
    args:
        user_id: str: candidat  id
        """
    response = requests.put(f"https://hr-api-endpoints.onrender.com/applications?id="+id, json=content)
    return str(response.status_code) + response.text
@tool
def update_applications(user_id):
    """create candidats from phone number
    args:
        user_id: str: candidat  id
        """
    response = requests.get(f"https://hr-api-endpoints.onrender.com/applications?id="+user_id)
    return str(response.status_code) + response.text
@tool
def get_job(job_id):
    """create candidats from phone number
    args:
        job_id: str: candidat  id
        """
    response = requests.get(f"https://hr-api-endpoints.onrender.com/job_description?id="+job_id)
    return str(response.status_code) + response.text
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=5,
)
tools=[]
tools_structure=[get_candidat,get_applications,get_job, update_applications]
memory = ConversationBufferMemory(
    memory_key="chat_history",  # must align with MessagesPlaceholder variable_name
    return_messages=True  # to return Message objects
)



prompt_analyse = ChatPromptTemplate.from_messages([
    ("system", """
        You are an expert HR analyst. Your task is to analyze a candidate's CV and an accompanying HR conversation transcript based on the provided job description.
        You should provide feedback and scores for the candidate's suitability, considering insights from BOTH the CV and the HR conversation.

        Please structure your response as a JSON object with the following keys:
        
            'education_summary': 'string',
            'education_scoring': 'string',
            'technicals_scoring': 'string',
            'technicals_summary': 'string',
            'experience_scoring': 'string',
            'experience_summary': 'string',
            'soft_skill_scoring': 'string',
            'soft_skill_summary': 'string',
            'additionnal_scoring': 'string',
            'additionnal_summary': 'string',
            'summary': 'string',
            'total_scoring': 'string'
            

        
    """),
     
     MessagesPlaceholder(variable_name="chat_history"),
    ("human", """
    Here is the CV text:
        get the cv text using the tool extract_from_cv 
    Here is the job description:
        get the user applications using his phone number and the get the job description using the tool get_job

        Here is the HR conversation transcript:
        {hr_conversation}
        
        Then update the application using the tool update_application and using the job description id"""),
    (MessagesPlaceholder(variable_name="agent_scratchpad")),
    ("placeholder", "{agent_scratchpad}"),
    
])
prompt_analyse.input_variables = ["hr_conversation","agent_scratchpad"]
#    ("system", "You're an HR professional.\nYour task is to extract and transcribe every piece of information from a resume into a JSON object with the following structure:\n- name: Full name of the candidate.\n- email: Email address.\n- phone: Phone number.\n- profile: A summary of the candidate's professional profile, including inferred information if relevant (e.g., years of experience, domain of expertise).\n- education: A list of objects, each containing:\n - school: Name of the institution.\n - degree: Name of the degree or program.\n - dates: Period of study.\n - description: Description of the curriculum or focus.\n - additional: Any extra inferred info or interesting details.\n- experience: A list of objects, each containing:\n - company: Name of the company.\n - position: Job title.\n - dates: Period of employment.\n - responsibilities: Description of the work done, ideally as a list.\n - additional: Any extra inferred info, technologies used, or interesting context.\n- technical_skills: All technical skills mentioned or inferred (e.g., programming languages, tools, platforms).\n- soft_skills: All soft skills mentioned or inferred (e.g., communication, leadership, teamwork).\n- additional: Any certificates, languages spoken, volunteering, interests, or other notable information.\nEach section must be fully completed with all relevant data from the resume, and you are allowed to infer or deduce information that is obvious based on context.\nIn each key (profile, education, experience, etc.).\nReturn ONLY the JSON object with no introduction, no explanation, and no extra text.\nMake sure the JSON is valid and can be parsed directly with json.loads().Don't add json at the beggining. "),

prompt = ChatPromptTemplate.from_messages([
    #("system", "you're an RH and your work is to transcript every information from the resume into a json that contains this information: name, email, phone, profile, education, experience, technical skills, soft skills, and additional.Everythink should be transcripted. In each key, you can add some information that seems obvious and add a question part with some questions that can be interesting to ask the candidate to complete this part. For any experience it should be a json that contains: company, position, dates, responsibilities, and additional. For any education it should be a json that contains: school, degree, dates, description, and additional. Don't add json at the beggining. Make sure that the return is a json that work with json.loads() and ther's nothing else as the answer then the json."),
    ("system", "You're an HR professional.\nYour task is to extract and transcribe every piece of information from a resume into a JSON with the following structure:\n first_name: First name of the candidate.\n- last_name: last name of the candidate.\n-address: address if exist.\n-email: Email address.\n- phone: Phone number that should like +33xxxxxxxxx withoun 0 or (0) after the +33 and without any space.\n- profile: A summary of the candidate's professional profile, including inferred information if relevant (e.g., years of experience, domain of expertise).\n- education: A list of objects, each containing:\n - school: Name of the institution.\n - degree: Name of the degree or program.\n - dates: Period of study.\n - description: Description of the curriculum or focus.\n - additional: Any extra inferred info or interesting details.\n- experience: A list of objects, each containing:\n - company: Name of the company.\n - position: Job title.\n - dates: Period of employment.\n - responsibilities: Description of the work done, ideally as a list.\n - additional: Any extra inferred info, technologies used, or interesting context.\n- technical_skills: All technical skills mentioned or inferred (e.g., programming languages, tools, platforms).\n- soft_skills: All soft skills mentioned or inferred (e.g., communication, leadership, teamwork).\n- additional: Any certificates, languages spoken, volunteering, interests, or other notable information.\nEach section must be fully completed with all relevant data from the resume, and you are allowed to add information that is obvious based on context. Make sure to not add json at the beggining"),
    (MessagesPlaceholder(variable_name="chat_history")),
    ("human", " the resume is {cv} "),
    (MessagesPlaceholder(variable_name="agent_scratchpad")),
    ("placeholder", "{agent_scratchpad}"),
])
prompt.input_variables = [ "cv","agent_scratchpad"]


agent = create_tool_calling_agent(
    llm=llm, tools=tools, prompt=prompt
    )

agent2 = create_tool_calling_agent(
    llm=llm, tools=tools_structure, prompt=prompt_analyse
    )

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)
agent_executor_analyse = AgentExecutor(
    agent=agent2,
    tools=tools,
    memory=memory,
    verbose=True
)
#"Job_description": "Vos missions au quotidien\nVous êtes passionné ! Vous souhaitez intégrer une équipe stimulante et prendre part activement aux défis qu’elle a à relever. Rejoignez-nous !\n\nAu sein du département des MODÈLES de la direction des risques du Groupe, le service de modélisation et data science assure le développement et la maintenance des modèles de risque de crédit, en conformité avec les réglementations en vigueur et les normes Groupe. Au sein du service de modélisation et data science, l’équipe de recherche, développement et méthodologies met en place des méthodologies et des outils innovants pour renforcer l’efficacité de la modélisation. En participant à ces activités, vous contribuerez à des enjeux stratégiques pour notre Banque.\n\nEn collaborant avec une diversité d’interlocuteurs, du front-office aux régulateurs, vous jouerez un rôle central dans l’optimisation des processus de modélisation, tout en faisant partie d'un environnement innovant et stimulant.\n\nVous intègrerez l’équipe de recherche, développement et méthodologies notamment en charge du développement d’outils intégrant l’Intelligence Artificielle (IA) Générative pour les besoins de la modélisation du risque de crédit.\n\nDans sa mission de recherche et développement, notre équipe joue un rôle stratégique en collaborant étroitement avec des partenaires clés tels que les modélisateurs et Data Lab du Groupe, la Direction Informatique, les front-offices et les départements spécialisés dans la gestion des risques, incluant le risque de marché, opérationnel et de crédit. Les outils que nous développons servent à optimiser l’efficacité et la qualité des processus de modélisation qui sont soumis à des revues rigoureuses par nos équipes d’audit interne et par des régulateurs de premier plan, tels que la BCE et l’ACPR. Cette démarche garantit la qualité et la conformité de nos process et modèles, tout en renforçant notre position en tant qu’acteur de confiance au sein de la Banque.\n\nConcrètement, vous serez amené, sous la supervision de votre tuteur et/ou votre manager, à :\n\nIdentifier les dernières avancées en matière d'IA générative et explorer comment ces technologies pourraient être appliquées à la modélisation du risque de crédit.\nRéaliser une revue approfondie sur l’exploitation des Large Langage Model (tokenisation, entraînement, validation).\nS'approprier la plateforme d’IA Générative interne et proposer des méthodes d’entraînement et/ou d’optimisation des modèles Large Language Models (LLM) intégrés.\nConcevoir et mettre en œuvre un Proof of Concept (POC) pour l'application de l'IA générative à un cas d'utilisation retenu (e.g. assistant de développement et documentation de codes, veille réglementaire, optimisation des processus de développement de modèles, etc.), en utilisant des outils et des techniques appropriés.\nEt si c’était vous ?\nVous allez préparer un Bac +4/5 en école de Commerce, d'Ingénieur ou Université avec une spécialisation en data science ou en informatique spécialité Data et intelligence artificielle.\nVous avez de solide compétences solides en programmation (Python, PySpark, R, etc.).\nVous connaissez des plateformes Cloud, notamment Azure, environnement Linux. C'est un plus !\nVous avez des connaissances en apprentissage automatique et traitement du langage naturel (NLP). c'est tout à votre avantage !\nVous comprenez les architectures de modèles LLM (Large Langue Model).\nVous avez de bonnes capacités rédactionnelles.\nVous êtes autonome, curieux, proactif.\nVous avez un bon esprit d’analyse et de synthèse ainsi que l'esprit d’équipe.\nYou’re fluent in english ! Vous êtes notre candidat idéal !\n\nPensez à accompagner votre CV de votre planning de formation.\n\nPlus qu’un poste, un tremplin\nRejoignez-nous pour faire grandir vos ambitions ! Dès votre arrivée, vous serez intégré dans nos équipes et apprendrez chaque jour aux côtés de nos experts qui vous accompagneront dans vos missions. Progressivement, vous gagnerez en autonomie sur vos projets pour faire de cette expérience un vrai accélérateur de carrière. Vous découvrirez également toute la diversité de nos métiers, dans un secteur qui évolue et innove en permanence. A la fin de vos études, diverses opportunités pourront s’offrir à vous, en France et à l’international.\n\nPourquoi nous choisir ?\nAttentif à votre qualité de vie et conditions de travail, vous bénéficiez d’avantages :\n\nPrime* de participation et d’intéressement\nJours de télétravail (selon le rythme de votre service et celui de votre alternance)\nPrise en charge de 50% de votre titre de transport\nBilletterie à prix réduits de notre Comité d’Entreprise (concerts, cinéma, sport…).\nOffre variée de restaurants d’entreprise et de cafétérias à tarifs compétitifs ainsi que des titres restaurants dématérialisés quand vous êtes en télétravail\n*Si vous avez 3 mois d’ancienneté sur l’exercice de référence\n\nCréer, oser, innover, entreprendre font partie de notre ADN. Si vous aussi vous souhaitez être dans l’action, évoluer dans un environnement stimulant et bienveillant, vous sentir utile au quotidien et développer ou renforcer votre expertise, nous sommes faits pour nous rencontrer !\n\nVous hésitez encore ?\n\nSachez que nos collaborateurs peuvent s’engager quelques jours par an pour des actions de solidarité sur leur temps de travail : parrainer des personnes en difficulté dans leur orientation ou leur insertion professionnelle, participer à l’éducation financière de jeunes en apprentissage ou encore partager leurs compétences avec une association. Les formats d’engagement sont multiples.",
def execute_agent( cv):
    out = agent_executor.invoke({
        'cv': cv,
        "chat_history": memory.chat_memory.messages,
    })
    print(out)
    return out["output"].replace('"','\"')

def execute_agent_analyse( hr_conversation):
    out = agent_executor_analyse.invoke({
       
        'hr_conversation': hr_conversation,
        "chat_history": memory.chat_memory.messages,
    })
    print(out)
    return out["output"]


