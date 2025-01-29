
import streamlit as st
from data import schools, majors
from functions import *


# SESSION STATE INITIALIZERS
    # If not found in st.session_state, create them (similar to class attributes)

# Student profile for LLM context (Students/Counselors)
if "student_profile" not in st.session_state:
    st.session_state.student_profile = initialize_random_profile()

# List of messages to hold the conversation
    # since we will be using a streamlit object to hold messages
        # messages will be appened as dictionary {"role":"user", "Content":"user_message"}
if "messages" not in st.session_state:
    st.session_state.messages = []

# Holds current turn count
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

# Holds max turn count
if "max_turns" not in st.session_state:
    st.session_state.max_turns = 10

# Flag to indicate looping state
if "active_looping" not in st.session_state:
    st.session_state.active_looping = False

# SIDEBAR LOGIC

# Sidebar header
st.sidebar.header("Student Profile")

# Variable for calling the student profile
profile = st.session_state.student_profile

# Editable sidebar fields, data capture fields for passing context
    # And grabbing ensuring we query the correct articulation agreements
# Name
with st.sidebar.expander("Name", expanded=True):
    name = st.text_input("Enter Name", value=profile["name"])
with st.sidebar.expander("Completed Courses"):
    completed_courses = (profile["completed_courses"])
# Current School
with st.sidebar.expander("Current School"):
    current_school = st.selectbox("Enter Current School", schools, index=schools.index(profile["current_school"]))
# GPA
with st.sidebar.expander("G.P.A."):
    gpa = st.number_input("Enter G.P.A.", min_value=0.0, max_value=4.0, step=0.1, value=round(profile["gpa"], 2))
# Major
with st.sidebar.expander("Major"):
    major = st.selectbox("Enter Major", majors, index=majors.index(profile["major"]))
# Transfer Schools
with st.sidebar.expander("Transfer Schools"):
    transfer_school = st.multiselect("Enter Transfer School(s)", schools, default=profile["transfer_school"])

# Transfer Schools
with st.sidebar.expander("Transfer Schools"):
    transfer_school = st.multiselect("Enter Transfer School(s)", schools, default=profile["transfer_school"])
# Goals
with st.sidebar.expander("Goals"):
    goals = st.multiselect("Enter Goal", profile['goals'],default=profile["goals"])
# notes
with st.sidebar.expander("notes"):
    notes = (profile["notes"])


# Functions to display custom text field buttons
def display_profile_field(field_name, field_label):
    with st.sidebar.expander(f"{field_label}"):
        # Dropdown menu to select an item
        if st.session_state.student_profile[field_name]:
            selected_index = st.selectbox(
                f"Select a {field_label[:-1]} to view or delete:",
                options=range(len(st.session_state.student_profile[field_name])),
                format_func=lambda i: st.session_state.student_profile[field_name][i],
                key=f"{field_name}-dropdown"
            )

            # Option to delete the selected item
            if st.button(f"Delete Selected {field_label[:-1]}", key=f"delete-{field_name}-btn"):
                st.session_state.student_profile[field_name].pop(selected_index)
                st.rerun()
        else:
            st.write(f"No {field_label.lower()} found.")

        # Input to add a new item
        new_item = st.text_input(f"Add a new {field_label[:-1]}:", key=f"new-{field_name}-input")
        if st.button(f"Add {field_label[:-1].capitalize()}", key=f"add-{field_name}-btn"):
            if new_item.strip():  # Avoid adding empty items
                st.session_state.student_profile[field_name].append(new_item.strip())
                st.rerun()

# Consolidate all fields into a single section
with st.sidebar.expander("Manage Profile Details"):
    display_profile_field("notes", "Notes")
    display_profile_field("completed_courses", "Completed Courses")

# Hardcoded checks
profile['current_school']="Merced College"
profile['transfer_school']=["University of California, Merced"]
profile['major']="Computer Science and Engineering, B.S."
current_school=profile['current_school']
transfer_school=(profile['transfer_school'])
major=profile['major']

# Update profile with changes
profile.update({
    "name": name,
    "current_school": current_school,
    "gpa": gpa,
    "major": major,
    "transfer_school": transfer_school,
    "notes": notes,
    "completed_courses": completed_courses,
    "goals": goals,
    "education_plan": []
})

# Initial message
    # This is used as an intial prompt/conversation starter
initial_message = (
    f"Hello, I am {profile['name']}. My major is {profile['major']}. "
    f"I currently attend {profile['current_school']} with a GPA of {profile['gpa']}. "
    f"I would like to transfer to {'; '.join(profile['transfer_school'])}. "
    f"Notes: {'; '.join(profile['notes'])}. "
)

# intial prompt for sidebar
    # Sperate from the others so that the when [profile]changes are applied and streamlit reruns
    # the intial message is updated which will update the intial prompt
    # Intial prompt is necessary if we wish to structure intial message to LLM beyond simple profile changes.
with st.sidebar.expander("Initial Prompt", expanded=False):
    initial_prompt = st.text_area("Edit Prompt", value=initial_message)

[{
	"resource": "/workspaces/assistPPM/test.py",
	"owner": "python",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pyright/blob/main/docs/configuration.md",
			"scheme": "https",
			"authority": "github.com",
			"fragment": "reportUndefinedVariable"
		}
	},
	"severity": 4,
	"message": "\"completed_courses\" is not defined",
	"source": "Pylance",
	"startLineNumber": 128,
	"startColumn": 26,
	"endLineNumber": 128,
	"endColumn": 43
}]


# CHAT CONTAINER

# Title
st.title("Test")

# Display the initial prompt if it's the first interaction
    # Updates with intial message changes
    # Sends on "next interaction" button push
    
# FIRST TURN LOGIC
if st.session_state.turn_count == 0:
    
    # Intial prompt subheader
    st.subheader("Initial Prompt")
    
    # Displays but doesnt appened intial message so we can edit it further 
    display_message("user", initial_message, "student.png")

# Display all messages from session state history on rerun
for message in st.session_state.messages:
    # dictionary with metadata helps display approritate with a helper funciton 
    avatar = "student.png" if message["role"] == "user" else "teacher.png"
    content = message["content"].strip()  
    display_message(message["role"], message["content"], avatar)   

# Logic to prevent use from running if user set max turns is excedded 
if st.session_state.turn_count >= st.session_state.max_turns:
    st.markdown("MAX TURNS TAKEN")
        

# if prompt with chat input
if prompt := st.chat_input("Type your message here"):
    
    ## WE NEED TO ADD FIRST TURN LOGIC HERE TO APPEND INTIAL PROMPT NO MATTER WHAT WE PUT INTO TEXT FIELD
    
    # Counselor's turn
    if st.session_state.turn_count % 2 != 0:
        # Add counselor message to chat history
        st.session_state.messages.append({"role": "assistant", "content": prompt})
        display_message("Counselor", prompt, "teacher.png")
        
        # increment turn counter
        st.session_state.turn_count += 1

        # Generate student response
        # st.spinner to indicate progress 
        with st.spinner("The student is thinking..."):
            # uses chat input and profile for context to generate student response
                # this is if we were to input chat as a counselor
            response = student(prompt, profile)
        # Add student message to chat history
        st.session_state.messages.append({"role": "user", "content": response})
        display_message("user", response, "student.png")
    
    else:  
        # Student's turn
        # Add student message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_message("user", prompt, "student.png")
        # increment turn counter
        st.session_state.turn_count += 1

        # Generate counselor response
        with st.spinner("The counselor is thinking..."):
            # uses chat input and profile for context to generate counselor response
                # this is if we were to input chat as a student
            agreement=get_articulation_agreement(current_school, transfer_school, major)
            response = advisorStep(prompt, profile, agreement)
        # Add Counselors message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        display_message("Counselor", response, "teacher.png")

    # Increment the loop counter for counseler/student response as we exit loop
    st.session_state.turn_count += 1

    
# BUTTON LOGIC

#columns for organizing buttons    
col1, col2, col3 = st.columns([0.3, 0.3,0.3])

# Step button logic (Used to take a  single turn)
with col1:
    
    if st.button('Step'):
    
        # Prevents the button from taking any action if turn count exceeds max turns
        while st.session_state.turn_count >= st.session_state.max_turns:
            st.rerun()

        # FIRST TURN LOGIC
        if st.session_state.turn_count == 0:
        
            with st.spinner("The counselor is thinking..."):
                agreement=get_articulation_agreement(profile['current_school'], profile['transfer_school'], profile['major'])
                print(agreement)
                intial_response = (advisorStep(initial_message, profile,agreement))
                st.session_state.messages.append({"role":"user", "content": initial_message})
                st.session_state.turn_count += 1
                st.session_state.messages.append({"role": "assistant", "content": intial_response})
                st.session_state.turn_count += 1
                
        # Student turn  
        elif (st.session_state.turn_count % 2) == 0:
            with st.spinner("The student is thinking..."):
                studentResponse = (student(st.session_state.messages[-1]["content"], profile))
                st.session_state.messages.append({"role":"user", "content": studentResponse})
                st.session_state.turn_count += 1
                
        # Counselor turn    
        elif (st.session_state.turn_count % 2) != 0:
            with st.spinner("The counselor is thinking..."):
                agreement=get_articulation_agreement(profile['current_school'], profile['transfer_school'], profile['major'])
                counselorResponse = (advisorStep(st.session_state.messages[-1]["content"], profile,agreement))
                st.session_state.messages.append({"role":"assistant", "content": counselorResponse})
                st.session_state.turn_count += 1
                
        st.rerun()
    
    


# Loop Button
with col2:
    if st.button("Loop"):
        # Flags loop state
        st.session_state.active_looping = True
        # Reruns streamlit to enter with loop logic
        st.rerun()
    
with col3:        

    if st.button("Stop"):
        # Flags loop state to stop looping
        st.session_state.active_looping = False
    

with col1:
    # Current turn counter
    st.write(f"Current turn: {st.session_state.turn_count + 1}")

with col2:
    # Max turn counter
    st.write(f"Max turns: {st.session_state.max_turns}")

with col3:
    # Max turn setter
    max_turns = st.number_input("Max Turns: ", min_value=1, max_value=10, step=1, value=st.session_state.max_turns)
    
# Indicates changes to max turns app reruns
if st.session_state.max_turns != max_turns:
    st.session_state.max_turns = max_turns
    st.rerun()
        
# LOOP STATE LOGIC
if st.session_state.active_looping == True:
    
    # loops while turn count is less than max turn 
    while st.session_state.turn_count < st.session_state.max_turns:
        
        # First turn logic (0 based index)
        if st.session_state.turn_count == 0:
            
            # spinner to indicate message progress
            with st.spinner("The counselor is thinking..."):
                
                # defines counselor response based on intial message as input, student profile as context
                agreement=get_articulation_agreement(profile['current_school'], profile['transfer_school'], profile['major'])
                counselorResponse = (advisorStep(initial_message, profile, agreement))
                
                # Add's users message to conversation list
                st.session_state.messages.append({"role":"user", "content": initial_message})
                
                # Incremnet turn counter
                st.session_state.turn_count += 1
                
                # Add's counselors message to conversation list
                st.session_state.messages.append({"role":"assistant", "content": counselorResponse})
                
                # increment turn counter
                st.session_state.turn_count += 1
        
        # Counselor's turn logic
        elif (st.session_state.turn_count % 2) != 0:
            
            # spinner to indicate message progress
            # consider removing the others as they may be extra 
            with st.spinner("The counselor is thinking..."):
                
                # defines counselor response based on previous message as input, student profile as context
                agreement=get_articulation_agreement(profile['current_school'], profile['transfer_school'], profile['major'])
                counselorResponse = (advisorStep(st.session_state.messages[-1]["content"], profile, agreement))
                
                # Add's counselors message to conversation list
                st.session_state.messages.append({"role":"assistant", "content": counselorResponse})
                
                # increment turn counter
                st.session_state.turn_count += 1
    
        # Student's turn logic
        elif (st.session_state.turn_count % 2) == 0:
            
            # spinner to indicate message progress
            with st.spinner("The student is thinking..."):
                
                # defines student response based on previous message as input, student profile as context 
                studentResponse = (student(st.session_state.messages[-1]["content"], profile))
                
                # Add's users message to conversation list
                st.session_state.messages.append({"role":"user", "content": studentResponse})
                
                # increment turn counter
                st.session_state.turn_count += 1
        
        # If turn counter exceeds max turn we change loop flag to stop     
        if st.session_state.turn_count >= st.session_state.max_turns:
            st.session_state.active_looping = False
    
        st.rerun()    