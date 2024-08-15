# Synthetic-data-generation
This repository contains a Streamlit application that generates synthetic tabular data using LLMs, respecting the constraints defined by the user.

# Constraints Defined by the User
There are two types of constraints that users can define:

**1. Column Constraints:** These include parameters such as column type, numerical distribution, and text format. Users can specify these constraints in an Excel sheet.

**2. Additional Constraints:** Users can define extra constraints in text form. For example:

"I want my dataset to contain 400 rows."
"I want a linear correlation between column A and column B."
# Customizing Synthetic Data
You can customize the synthetic data using the chat bar. Here, you can send prompts to the application to make additional changes or correct any issues from the initial data generation.

# Visualizing Data with ChatViz
The ChatViz feature allows you to plot graphs and visualize the dataset to verify whether the synthetic data adheres to the statistical constraints defined initially.
