import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Functions to get profile data
def get_id(query='albert einstein'):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://www.personality-database.com',
        'priority': 'u=1, i',
        'referer': 'https://www.personality-database.com/',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Brave";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'x-lang': 'en-US',
        'x-tz-database-name': 'America/Sao_Paulo',
    }

    params = {
        'query': query,
        'limt': '10',
        'nextCursor': '0',
        'pid': '0',
        'catID': '0',
    }

    response = requests.get('https://api.personality-database.com/api/v2/search/profiles', params=params, headers=headers)
    return int(json.loads(response.content)['data']['results'][0]['id'])

def get_pdb_data(profile=55341):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.8',
        'origin': 'https://www.personality-database.com',
        'priority': 'u=1, i',
        'referer': 'https://www.personality-database.com/',
        'sec-ch-ua': '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'x-lang': 'en-US',
        'x-tz-database-name': 'America/Sao_Paulo',
    }

    response = requests.get(f'https://api.personality-database.com/api/v1/profile/{profile}', headers=headers)
    dictionary = json.loads(response.content)
    if 'code' in dictionary:
        st.error(f'{profile} not found')
    else:
        return dictionary

# Function to process data for overview
def process_data(sample):
    
    all_data_df = {}
    for col in sample.columns[1:]:
        vote_counts = {}
        for row, votes in enumerate(sample[col]):
            character = sample.index[row]
            vote_counts[character] = {vote['myValue']: vote['theCount'] for vote in votes}
        vote_counts_df = pd.DataFrame(vote_counts).transpose()
        all_data_df[col] = vote_counts_df

    return all_data_df

def get_most_likely_mbti(df):
    
    mbti_df = df.copy()
    mbti_df['prob_E'] = None
    mbti_df['prob_N'] = None
    mbti_df['prob_T'] = None
    mbti_df['prob_P'] = None
    mbti_df['prob_MBTI'] = None
    for row in range(len(mbti_df)):
        df1 = mbti_df.iloc[row].to_frame().rename(columns={mbti_df.iloc[row].to_frame().columns[0]: 'votes'})
        df1['E_I'] = df1.index.str[0]
        if df1['votes'].sum() <= 10:
            continue
        # Count occurrences of E and I
        prob_E = df1[df1['E_I'] == 'E']['votes'].sum()/df1['votes'].sum()
        prob_I = df1[df1['E_I'] == 'I']['votes'].sum()/df1['votes'].sum()
        mbti_df['prob_E'].iloc[row] = prob_E

        df1['N_S'] = df1.index.str[1]
        # Count occurrences of N and S
        prob_N = df1[df1['N_S'] == 'N']['votes'].sum()/df1['votes'].sum()
        prob_S = df1[df1['N_S'] == 'S']['votes'].sum()/df1['votes'].sum()
        mbti_df['prob_N'].iloc[row] = prob_N

        df1['T_F'] = df1.index.str[2]
        # Count occurrences of T and F
        prob_T = df1[df1['T_F'] == 'T']['votes'].sum()/df1['votes'].sum()
        prob_F = df1[df1['T_F'] == 'F']['votes'].sum()/df1['votes'].sum()
        mbti_df['prob_T'].iloc[row] = prob_T

        df1['P_J'] = df1.index.str[3]
        # Count occurrences of P and J
        prob_P = df1[df1['P_J'] == 'P']['votes'].sum()/df1['votes'].sum()
        prob_J = df1[df1['P_J'] == 'J']['votes'].sum()/df1['votes'].sum()
        mbti_df['prob_P'].iloc[row] = prob_P

        personality = ''
        if prob_E >= 0.5:
            personality+='E'
        else:
            personality+='I'

        if prob_N >= 0.5:
            personality+='N'
        else:
            personality+='S'

        if prob_T >= 0.5:
            personality+='T'
        else:
            personality+='F'

        if prob_P >= 0.5:
            personality+='P'
        else:
            personality+='J'

        mbti_df['prob_MBTI'].iloc[row] = personality

    return mbti_df



def get_most_likely_enneagram(enneagram_df):
    
    new_enneagram_df = enneagram_df.copy()
    new_enneagram_df['prob_1'] = None
    new_enneagram_df['prob_2'] = None
    new_enneagram_df['prob_3'] = None
    new_enneagram_df['prob_4'] = None
    new_enneagram_df['prob_5'] = None
    new_enneagram_df['prob_6'] = None
    new_enneagram_df['prob_7'] = None
    new_enneagram_df['prob_8'] = None
    new_enneagram_df['prob_9'] = None
    new_enneagram_df['prob_Enneagram'] = None
    
    for row in range(len(new_enneagram_df)):

        df1 = new_enneagram_df.iloc[row].to_frame().rename(columns={new_enneagram_df.iloc[row].to_frame().columns[0]: 'votes'})
        
        if df1['votes'].sum() <= 10:
            continue

        wings = list(df1.index)
        prob_max = []
        for i in range(1, 10):
            votes_for_i = df1.loc[df1.index.str[0].isin([f'{i}']), 'votes'].sum()
            new_enneagram_df[f'prob_{i}'].iloc[row] = votes_for_i / df1['votes'].sum()
            prob_max.append([i,  new_enneagram_df[f'prob_{i}'].iloc[row]])

        most_likely_type = max(prob_max, key=lambda x: x[1])[0]
        most_likely_type_votes = df1.loc[df1.index.str.startswith(f'{most_likely_type}'), 'votes'].to_dict()
        most_likely_enneagram = max(most_likely_type_votes, key=most_likely_type_votes.get)
        new_enneagram_df['prob_Enneagram'].iloc[row] = most_likely_enneagram

    return new_enneagram_df

def get_most_likely_socionics(df):
    # Initialize columns for probabilities and the most likely Socionics type
    socionics_df = df.copy()
    socionics_df['prob_Socionics'] = None
    
    for row in range(len(socionics_df)):
        df1 = socionics_df.iloc[row].to_frame().rename(columns={socionics_df.iloc[row].to_frame().columns[0]: 'votes'})
        #print(row)
        if df1['votes'].sum() <= 10:
            continue
        values = ['E', 'I', 'S', 'L']
        prob_max = []
        for i in values:
            votes_for_i = df1.loc[df1.index.str[0].isin([f'{i}']), 'votes'].sum()
            prob_max.append([i,   votes_for_i / df1['votes'].sum()] )

        most_likely_type = max(prob_max, key=lambda x: x[1])[0]
        most_likely_type_votes = df1.loc[df1.index.str[0].isin([most_likely_type]), 'votes'].to_dict()
        prob_max2 = []
        for j in values:
        
            votes_for_i2 = df1.loc[most_likely_type_votes.keys()].loc[df1.loc[most_likely_type_votes.keys()].index.str[1].isin([f'{j}']), 'votes'].sum()
            #print( prob_max, most_likely_type, votes_for_i2 )
            prob_max2.append([j,   votes_for_i2 / df1.loc[most_likely_type_votes.keys()]['votes'].sum()] )


        most_likely_type2 = max(prob_max2, key=lambda x: x[1])[0]
        most_likely_type_votes2 = df1.loc[most_likely_type_votes.keys()].loc[df1.loc[most_likely_type_votes.keys()].index.str[1].isin([most_likely_type2]), 'votes'].to_dict()
        socionics_df['prob_Socionics'].iloc[row] = max(most_likely_type_votes2, key=most_likely_type_votes2.get)  
    
    return socionics_df

# Streamlit dashboard
st.title("Personality Database Analysis")

# Tab selection
tab1, tab2 = st.tabs(["Profile Search", "Overview Analysis"])

# Profile Search Tab
with tab1:
    st.header("Profile Search")
    
    query = st.text_input("Enter the profile name (e.g., 'albert einstein'):")
    
    if st.button("Search"):
        if query:
            try:
                profile_id = get_id(query=query)
                profile_data = get_pdb_data(profile=profile_id)
                
                if profile_data:
                    st.subheader(f"Profile Information: {profile_data['mbti_profile']}")
                    #st.json(profile_data)
                    # Visualize votes
                    for i in range(1,10):
                        try:
                            votes = pd.DataFrame(profile_data['breakdown_systems'][f'{i}'])[['personality_type', 'theCount']]#.set_index('personality_type')
                            typologies = ['MBTI', 'Enneagram', 'Socionics', 'Moral Alignement', 'Instinctual Variant', 
                                        'Tritype','Temperament', 'Attitudnal Psyque','Big Five']
                            if len(votes)>0:
                                st.subheader("Votes Breakdown")
                                # Create the bar plot using Plotly
                                fig = px.bar(
                                    votes, 
                                    x='personality_type', 
                                    y='theCount', 
                                    title='Distribution of Votes Values', 
                                    #labels={'prob_MBTI': 'MBTI Type', 'count': 'Count'},
                                    color='theCount',  # Coloring by count for better visualization
                                    color_continuous_scale=px.colors.sequential.Viridis  # You can choose other color scales as well
                                )

                                fig.update_layout(title=f'{typologies[i-1]} Votes', template='plotly_white', title_x=0.5)
                                st.plotly_chart(fig)
                                #st.bar_chart(votes.all(), x="personality_type", y="theCount")
                        except:
                            st.write("No votes data available.")
                        
            except Exception as e:
                st.error(f"Error retrieving profile: {str(e)}")
        else:
            st.warning("Please enter a profile name to search.")

# Overview Analysis Tab
with tab2:
    st.header("Overview of MBTI, Enneagram, and Socionics Typologies")

    # Sample data for demonstration
    sample_data =  pd.read_json('PDB_profiles_votes.json')
    sample_data = sample_data.sample(1000, random_state=123).reset_index(drop=True).set_index('name')
            
    all_data_df = process_data(sample_data)
    mbti_counts_df = all_data_df['mbti_votes'].drop(columns = 'XXXX')
    enneagram_counts_df = all_data_df['ngram_votes'].drop(columns = 'XXXX')
    socionics_counts_df = all_data_df['socionics_votes'].drop(columns = 'XXXX')

    new_socionics_df = get_most_likely_socionics(socionics_counts_df)
    new_enneagram_df = get_most_likely_enneagram(enneagram_counts_df)
    new_mbti_df = get_most_likely_mbti(df = mbti_counts_df)


    st.header("MBTI Analysis")
    st.write(new_mbti_df.head())

    # Correlation Heatmap
    st.subheader("MBTI Votes Correlation")
    correlation_matrix = mbti_counts_df.corr()
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale='Viridis',
        colorbar=dict(title='Correlation')
    ))
    fig.update_layout(title='MBTI Votes Correlation', template='plotly_white', title_x=0.5)
    st.plotly_chart(fig)

    # Bar Plot of MBTI Distribution
    st.subheader("Distribution of MBTI Values")
    prob_MBTI_counts = (new_mbti_df['prob_MBTI'].value_counts()/len(new_mbti_df['prob_MBTI'])).reset_index()
    prob_MBTI_counts.columns = ['prob_MBTI', 'count']
    fig = px.bar(prob_MBTI_counts, x='prob_MBTI', y='count', color='count', color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_layout(title={'x':0.5}, xaxis_title='MBTI Type', yaxis_title='Count', template='plotly_white')
    st.plotly_chart(fig)

    st.header("Enneagram Analysis")
    st.write(new_enneagram_df.head())

    # Correlation Heatmap
    st.subheader("Enneagram Votes Correlation")
    correlation_matrix = enneagram_counts_df.corr()
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale='Viridis',
        colorbar=dict(title='Correlation')
    ))
    fig.update_layout(title='Enneagram Votes Correlation', template='plotly_white', title_x=0.5)
    st.plotly_chart(fig)

    # Bar Plot of Enneagram Distribution
    st.subheader("Distribution of Enneagram Values")
    prob_NGRAM_counts = (new_enneagram_df['prob_Enneagram'].value_counts()/len(new_enneagram_df['prob_Enneagram'])).reset_index()
    prob_NGRAM_counts.columns = ['prob_Enneagram', 'count']
    fig = px.bar(prob_NGRAM_counts, x='prob_Enneagram', y='count', color='count', color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_layout(title={'x':0.5}, xaxis_title='Enneagram Type', yaxis_title='Count', template='plotly_white')
    st.plotly_chart(fig)

    st.header("Socionics Analysis")
    st.write(new_socionics_df.head())

    # Correlation Heatmap
    st.subheader("Socionics Votes Correlation")
    correlation_matrix = socionics_counts_df.corr()
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale='Viridis',
        colorbar=dict(title='Correlation')
    ))
    fig.update_layout(title='Socionics Votes Correlation', template='plotly_white', title_x=0.5)
    st.plotly_chart(fig)

# Add more interactive elements as needed
