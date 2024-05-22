from operator import itemgetter
import pandas as pd
from rich import print
from typing import List
import streamlit as st
from dotenv import load_dotenv
from htmlTemplates import bot_template, user_template, css
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
)
import traceback
import subprocess
import plotly.io as pio
from chat2plot import chat2plot
from dotenv import load_dotenv


load_dotenv()

class SynthData:

    def __init__(self):

        self.template = """Write some python code to solve and return the user's problem. 
                            Return only python code in Markdown format, e.g.: 
                            using numpy is case 
                            ```python
                            ....
                            ```"""
        self.chain = None
        self.chat_history = None
        self.dataspec = None 
        self.columns_description = None 
        self.response = None
        self.dataset = None


    def _sanitize_output(self, text: str):
        
        """  
        Args:
            llm_output (str): The LLM output string.

        Returns:
            str: The extracted code portion, ready to run.

        """

        _, after = text.split("```python")
        return after.split("```")[0]

    def generate_prompt(self, dataspec):

        """  
        Args:
            data_spec (DataFrame): The dataframe containing the description of each column.

        Returns:
            str: A prompt containing the data specification description.

        
        """

        dataspec = dataspec.set_index(dataspec['COLUMN_NAME'],drop=True).drop(['COLUMN_NAME'],axis = 1)
        columns_description= """"""

        for col in dataspec.index : 

            columns_description += col 
            columns_description+= """  Description:  """
            columns_description+= dataspec.loc[col].DESCRIPTION

            if str(dataspec.loc[col].MODALITIES) != 'nan' : 
                columns_description+= """ The column contain the respected Modalities : """ + str(dataspec.loc[col].MODALITIES)
            if str(dataspec.loc[col].FREQUENCIES).replace(' ','')!='nan':
                columns_description+= """ With the following Frequencies :  """ + str(dataspec.loc[col].FREQUENCIES)
            
            if str(dataspec.loc[col].FORMAT).replace(' ','') != 'nan':
                columns_description+= """ With the following FORMAT :  """ + str(dataspec.loc[col].FORMAT)

            columns_description+='\n'
            columns_description+='\n'

        columns_description+= """Important :  Make sure to respect all of this textuel and numeric constraints"""
        self.columns_description = columns_description

        return self.columns_description
    

    def create_chain(self):
        """Creates the LLM chain and initializes memory to start a conversation with the LLM model (e.g., GPT-3.5)."""

        prompt = ChatPromptTemplate.from_messages(
        [
            ("system", self.template),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
        )
        
        model =  ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
        memory = ConversationBufferMemory(return_messages=True)
        memory.load_memory_variables({})
        {'history': []}


        chain = (
            RunnablePassthrough.assign(
                history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
            )
            | prompt
            | model
            | StrOutputParser()    
        )

        self.chain = chain 
        self.chat_history = memory

        return self.chain,self.chat_history


    def handle_user_query(self, user_query):

        """  
        This function is designed to update the dataset according to the user query.

        Args:
        user_query (str): The query provided by the user.

        Returns:
        Data_updated

        """

    
        response2 = self.chain.invoke({"input": user_query})

        # Try if the code output is already with the correct form 
        try : 
            parser_output = self._sanitize_output(response2)
        
        except Exception as e : 
            parser_output = response2
    
        # Run the code
        self.execute_code(parser_output)
        dataset = pd.read_csv('fake_data.csv')
        self.dataset = dataset
        st.write(self.dataset)
        self.chat_history.save_context({"input": user_query}, {"output": response2})
        self.chat_history.load_memory_variables({})

        return dataset

    def execute_code(self, response):

        """ Extracts the code from the LLM output and saves it into a file named 'gpt_code.py', then executes the code. """

        print('write the code')
        file1 = open('gpt_code.py', 'w')
        s = response
        
        # Writing a string to file
        file1.write(s)
        
        # Writing multiple strings
        
        # Closing file
        file1.close()

        print('run the code writed using subprocess')
        result = subprocess.run(["conda", "run", "-n", "pdi", "python", "gpt_code" + ".py"], check=True)

        if result.returncode :
            print('code Done !')


    def run_code_with_debug(self, query,debug = False):
        """ This function is created to generate the first version of synthetic data """


        print("run query")
        response = self.chain.invoke({"input": query})
        self.chat_history.save_context({"input": query}, {"output": (response)})
        self.chat_history.load_memory_variables({})

        response_parser = self._sanitize_output(response)
        _,error_message = self.run_code_and_get_error(response_parser)
        
        print("Get llm response ")
        
        try : 
                response_parser = self._sanitize_output(response)
            
        except Exception as e : 

                response_parser = response
        print("Get the code from the llm response")

        # Debug the code 
        #(In order to avoid infinite loop, only set debug to True if you are sure that the code is running in your Python environment)
        if debug : 
        
            while error_message :

                print("debug")
                print(error_message)
                query1 = """ f \n I have this error  {error_message} fix it please"""
                response1 = self.chain.invoke({"input": query1})

                try : 
                    response_parser = self._sanitize_output(response1)
                
                except Exception as e : 

                    response_parser = response1

                _,error_message = self.run_code_and_get_error(response_parser)

                self.chat_history.save_context({"input": query1}, {"output": (response1)})
                self.chat_history.load_memory_variables({})
        

        print("run the code using execute_code")
        self.execute_code(response_parser)

    def generate_data(self, columns_description, additional_constraint):


        """ 
        Generates synthetic data based on the provided column descriptions and additional constraints.

        Args:
            columns_description (str): Description of the columns to be included in the synthetic data.
            additional_constraint (str): Additional constraint to be respected during data generation.

        Returns:
            pandas.DataFrame: DataFrame containing the synthetic data.

         """
        


        query = f"""Generate synthetic data using Python code with the following columns and their descriptions:

                {columns_description}

                and respect the additional constraint:

                {additional_constraint}

                Save the data to the following path: fake_data.csv
                """

        
        print('start run code with debug')
        self.run_code_with_debug(query)
        
        return pd.read_csv("fake_data.csv")

    def run_code_and_get_error(self, code):

        """   
        Executes the provided Python code and returns any error message encountered.

        Args:
            code (str): The Python code to be executed.

        Returns:
            Tuple[str, str]: A tuple containing the error message (if any) and the error string. If no error occurs, both elements of the tuple will be None.
        
        """

        try:

            # Ensure that the code is running in your Python environment to avoid false error messages.
            exec(code)
            return None, None  # No error occurred
        
        except Exception as e:
            error_message = traceback.format_exc()
            return error_message, str(e)  # Retu


    def ChatVis(self,user_query) : 

        """  
        Generates a visualization based on the user query and saves it as an image file.

        Args:
            user_query (str): The query provided by the user.

        Returns:
            None

        Example:
            If the user query is "Show me a histogram of age distribution", the function will generate a histogram based on the 'fake_data.csv' file and save it as 'figure.png'.
 
        """

        df = pd.read_csv('fake_data.csv')

        c2p = chat2plot(df)
        result_graph = c2p(user_query)

        pio.write_image(result_graph.figure, 'figure.png')