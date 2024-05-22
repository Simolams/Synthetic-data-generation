import poo 
from poo import *



engine_generator = SynthData()

def main():
    
    st.set_page_config(page_title='Chat with me ! to Generate and interact with synthetic datasets ! ', page_icon=':books:')

    st.write(css, unsafe_allow_html=True)
    
    if "chain" not in st.session_state:
        st.session_state.chain = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    st.header('SynthChat')
    
    user_query = st.text_input("Here, you can ask for anything to personalize your data!")

    if  (type(user_query) == str and len(user_query.replace(' ','')) != 0 ) and st.button('SEND'):

        user_query += """ \n  dont foregt to save it on the path fake_data.csv """
        if st.session_state.chat_history:
            st.session_state.chat_history.chat_memory.messages = st.session_state.chat_history.chat_memory.messages[:1]+st.session_state.chat_history.chat_memory.messages[-2:]
            
        try : 

            engine_generator.chat_history = st.session_state.chat_history 
            engine_generator.chain = st.session_state.chain
            dataset = engine_generator.handle_user_query(user_query)
            engine_generator.dataset = dataset
        except : 
            st.write('Something is wrong, please ask me again.')
         
        
        if st.button('Save Data as CSV'):

            # Save updated data as CSV
            dataset.to_csv('updated_data.csv', index=False)
            st.write('Data saved successfully as updated_data.csv!')
        

    st.header('ChatViz')
    query = st.text_input("Here, you can ask for anything make Visualisation") 
    
    if  (type(query) == str and len(query.replace(' ','')) != 0 ) and st.button('PLOT'):

        engine_generator.ChatVis(query)
        st.image('figure.png', caption='Image', use_column_width=True)
        
        
    

    with st.sidebar:
        st.subheader("Upload your Dataspec Here: ")
        dataspec_file = st.file_uploader("Choose your PDF Files and Press OK", type=['xlsx'], accept_multiple_files=False)
        print(dataspec_file)
        additional_constraint = st.text_input("Enter here the additional constraint")

        if st.button("OK") and (type(additional_constraint)==str and len(additional_constraint.replace(' ','')) !=0):
            with st.spinner("Processing your dataspec..."):
                
                # Get PDF Text
                dataspec = pd.read_excel(dataspec_file)


                # Get Text Chunks                
                columns_description  = engine_generator.generate_prompt(dataspec)
                

                # Create Vector Store
                print('start create chain')
                st.session_state.chain, st.session_state.chat_history =  engine_generator.create_chain()


                print("Start generate_data")
                
                dataset = engine_generator.generate_data(columns_description,additional_constraint)
                st.write(dataset)
                st.write("DONE")     
                dataset.to_csv('synthdata_first_version.csv', index=False)
   
                


if __name__ == '__main__':
    main()