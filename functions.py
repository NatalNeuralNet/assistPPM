from openai import OpenAI
import random
import streamlit as st
from data import *
from pydantic import BaseModel
from astrapy import DataAPIClient
from astrapy import Database, Collection
from itertools import product
from dotenv import load_dotenv
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(OPENAI_API_KEY)

# Load environment variables from the .env file
load_dotenv()

# Access the variables
TOKEN = os.getenv("TOKEN")
DB_API_ENDPOINT = os.getenv("DB_API_ENDPOINT")

# Database keyspace name
KEYSPACE_NAME = "test"

# Access astrapy client using token
clientb = DataAPIClient(TOKEN)

# Explicit keyspace
database = clientb.get_database(DB_API_ENDPOINT)

# Getting collection from database
collection = database.get_collection("COLLECTION_NAME3")

#Function for simulated student response
'''
Args:
    prompt (str): message that is being responded to
    profile (dict{str : *}): student profile to to give context to a system prompt dictating how a simulate student should act

Returns: 
    (str): response to prompt
'''
def student(prompt, student_profile):
    profile_description = (
        f"My name is {student_profile['name']}. "
        f"I am currently attending {student_profile['current_school']} with a GPA of {student_profile['gpa']}. "
        f"My major is {student_profile['major']}, and I plan to transfer to {(', ').join(student_profile['transfer_school'])}. "
        f"My motivation is {student_profile['motivation']}, and my challenges are {student_profile['challenges']}. "
        f"My characteristics are {student_profile['characteristics']}, and my goals are {(', ').join(student_profile['goals'])}."
    )
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are a student with the following profile: {profile_description}. Use this to inquire about your academic journey. Focus on your transfer journey"},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def advisorStep(prompt, student_profile, articulation_agreement):
    '''
    Args:
        prompt (str): message that is being responded to
        profile (dict{str : *}): student profile to to give context to a system prompt dictating how a simulate student should act
        agreement (dict{str : str}): articulation agreement passed to give accurate transfer suggestions
            this will be pulled from a database, as the couselor is giving advice only they need this passed not the student

    Returns: 
        (str): response to prompt
    '''
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are an academic advisor specializing in transfer students. You have access to their profile {student_profile} and transfer agreements for desired schools{articulation_agreement}"},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def initialize_student_profile():
    """
    - Initializes a student profile for streamlit display and data capature.
    - In the future this where we would create fields of bias testing.
    
    Args:
        None
        
    Returns:
        dict: Specified student profile dictionary
    """
    
    return {
        "name": "Aisha Jamal",
        "current_school": "Merced College",
        "gpa": 3.8,
        "major": "Computer Science, B.S.",
        "transfer_school": ["University of California, Merced", "California State University, Stanislaus"],
        "motivation": ["Interested in innovative, flexible computer science courses that fit her busy schedule", "Transferrable courses to Stanislaus State University, where she plans to finish up her degree"],
        "challenges": ["Concerned about time management and the flexibility of her study schedule around work and family commitments", "First-generation college student", "Works to contribute to the family income"],
        "characteristics": ["Needs clear, immediate applicability of learning to her job and future career goals", "Values collaborative projects and simulations that mimic real-world business challenges"],
        "goals": ["Complete a CS Associate degree program at Merced College while also being the CAHSI Advocate and completing a research experience for undergraduate (REU) in AI LLM Research", "Provide for her family while investing in her career advancement"],
    }
    
# Pydantic strucuted output for OpenAI model generated profile fields 
class profileGenerator(BaseModel):
    motivations: list[str]
    challenges: list[str]
    characteristics: list[str]
    goals: list[str]


def generate_field_via_gpt(student_profile):
    
    """
    - OpenAI model generates randomized open ended text fields with relevant responses 
    - Although context is passed it is ultimately not utilized in this implementation so it should be removed to cut down on token costs
        - In future studies this can be used as a way to to pass natural bias skewing data fields like sex, gender, or ethnicity
            - to see how a model might generate different goals given these fields
    
    Args:
        student_profile (dict): Student profile context for generating "In Character" fields
        
    Returns:
        dict: A dictionary containing the randomized student profile adhering to pydantic schema to ensure strucuted output.
    """
    
    context_description = (
        f"My name is {student_profile['name']}. "
        f"I am attending {student_profile['current_school']} with a GPA of {student_profile['gpa']}. "
        f"My major is {student_profile['major']}, and I plan to transfer to {', '.join(student_profile['transfer_school'])}."
    )

    completion = client.beta.chat.completions.parse(
        
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an expert at profile field generation. You will \
                                        be given college student profile fields and should generate relevant fields it into the given structure."},
            {"role": "user", "content": "..."}
        ],
    response_format=profileGenerator,
)

    return completion.choices[0].message.parsed
  
def initialize_random_profile():
    """
    -Unitializes a random student profile with fields populated using ChatGPT.
    -This is used to test random scenarios and simulate Student profiles and testing.
    -Easier randomized data field entries such as pick a selection from a list randomly 
        -are handled here to prevent unnecessary LLM processing in needing to do such.
    -Utilizes the generate_field_via_gpt function for randomized text entries.
    
    Args:
        None
        
    Returns:
        dict: A dictionary containing the randomized student profile.
    """
    # Basic randomized fields
    random_name = random.choice(["Aisha Jamal", "John Doe", "Emily Nguyen", "Carlos Perez"])
    random_school = random.choice(schools)
    random_gpa = round(random.uniform(0.0, 4.0), 2)
    random_major = random.choice(majors)
    random_transfer_schools = random.sample(schools, 2)

    
    # Context for field generation
        # Consdier removing as we dont use this as context
    profile_context = {
        "name": random_name,
        "current_school": random_school,
        "gpa": random_gpa,
        "major": random_major,
        "transfer_school": random_transfer_schools
    }

    # Generate text fields using ChatGPT
    fields = generate_field_via_gpt(profile_context)


    # Assign the indvidual generated text fields
    motivations = fields.motivations
    challenges = fields.challenges
    characteristics = fields.characteristics
    goals = fields.goals

    # Return the randomized profile
    return {
        "name": random_name,
        "current_school": random_school,
        "gpa": random_gpa,
        "major": random_major,
        "transfer_school": random_transfer_schools,
        "motivation": motivations,
        "challenges": challenges,
        "characteristics": characteristics,
        "goals": goals,
    }

    
def display_message(role, content, avatar):
    """
    Organizes a streamlit chat container, utlizing columns to display a message with corresponding avatars and content.

    Args:
        role (str): Role of the speaker ('Student' or 'Counselor').
        content (str): Content of the message to be displayed.
        avatar (str): Path to the avatar image.
        
    Return: Void display organization only
    """
    if role == "user":
        col1, col2 = st.columns([0.9, 0.1])
        # Avatar on the right
        with col2:
            st.image(avatar, width=40)
        # Message content on the left
        with col1:
            st.markdown(f"**Student:** \n\n{content.strip()}")
    # For 'Counselor'
    else: 
        col1, col2 = st.columns([0.1, 0.9])
        # Avatar on the left
        with col1:
            st.image(avatar, width=40)
        # Message content on the right
        with col2:
            st.markdown(f"**Counselor:** \n\n{content.strip()}")
    # Line divider
    st.divider()
    
    
# Function to get articulation agreements from a database
def get_articulation_agreement(current_school, transfer_school, major):
    """
    -Retrieves specific articulation agreements based on Student entered data fields in Streamlit.
    -Front End data entry ensure we pass the correct context to the LLM and bypasses unstrucuted conversational parsing .
    -Handles cases where `transfer_schools` and `majors` are lists. In case Students wish to query multiple agreements.
        -Traditional tools like Assit.org allow for one query at a time 
            -if we follow suit we will have a more focused answer from the llm in passing only one agreement.
        -Perhaps this is an area where our methods show improvements on traditional methods 
            -so I think we want a limit on multiple agreements rather than stopping multiple agreements.
        -Limits of this method include the complex scneraio of a student attenting two current schools.
    
        Args:
        current_school (str): A Students current school.
        transfer_school (list[str]): A Student's desired transfer school(s).
        major (str): A student's desired major(s).
        
        Return (dict{str : str}): A dictionary is returned with an articulation agreement key and a database query value
            If no agreement is found, such key is appened instead of an articulation agreement 
    """
    
    test =[]
    
    # Ensure `incoming` and `major` are lists for proccessing
    transfer_school_list = transfer_school if isinstance(transfer_school, list) else [transfer_school]
    major_list = major if isinstance(major, list) else [major]

    # Query for each combination
    for incoming_college, major_item in product(transfer_school_list, major_list):
        query = {
            "$and": [
                {"incoming": incoming_college},
                {"outgoing": current_school},
                {"major": major_item}
            ]
        }
        try:
            # Execute query
            results = collection.find(query, projection={
                "incoming": True,
                "outgoing": True,
                "major": True,
                "text": True
            })

            # Flag for indicating if an agreement was found 
            found = False
            # Iterate through results
            for result in results:
                found = True
                text = result.get('text', 'No description available')
                test.append({
                    text: f"{result['outgoing']} to {result['incoming']} for {result['major']}"
                })
            
            # If no results were found
            if not found:
                test.append({
                    f"No agreement for {incoming_college}": f"{current_school} with major {major_item}"
                })

        except Exception as e:
            # Handle query exceptions
            test.append({
                "Error querying articulation agreements": 
                f"Query failed for {incoming_college} to {current_school} with major {major_item}: {e}"
            })

    return test
