import streamlit as st
import llm_model
import html_scrapping


st.set_page_config(page_title="Lead Generation")

# Sidebar contents
with st.sidebar:
    st.title("💬 Lead Generation")
    st.markdown(
        """
    ## About    
    💡 List of leads generated by Algorithm Dimension for Kara
    """
    )

user_input = st.text_input("Enter the url of the job postings page:")

if user_input:
    st.write(f"Searching for customers of {user_input}...")

    print("We are scrapping text data")
    html_raw_code = html_scrapping.extract_readable_text(user_input)
    print("HTML_raw_code = ", html_raw_code)
    print("Scrapping is done")
    print("GPT 3.5 is Working")
    response = llm_model.find_job_list_url("fr.indeed.com", html_raw_code)
    st.write(response)