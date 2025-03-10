import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import os

# Define font paths
emoji_font_path = r"C:\\Windows\\Fonts\\seguiemj.ttf"  # Segoe UI Emoji for emojis

# Function to set fonts safely
def set_matplotlib_font(font_path):
    if os.path.exists(font_path):
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams["font.family"] = font_prop.get_name()
    else:
        st.warning(f"Font file not found: {font_path}. Using default font.")

st.sidebar.title("Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    
    # Debug: Check if DataFrame is empty
    if df.empty:
        st.error("Error: No data was loaded. Please check the file format.")
        st.stop()
    
    # Debug: Display column names and first few rows
    st.write("Columns in DataFrame:", df.columns)
    st.write("First 5 rows:", df.head())
    
    # Extract user list
    user_list = df['user'].dropna().unique().tolist()
    user_list = [user for user in user_list if user not in ["group_notification", ""]]
    user_list.insert(0, "Overall")
    
    # Debug: Display extracted users
    st.write("Extracted Users:", user_list)
    
    selected_user = st.sidebar.selectbox("Show analysis for", user_list)
    
    if st.sidebar.button("Show Analysis"):
        st.title("Top Statistics")
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Messages", num_messages)
        col2.metric("Words", words)
        col3.metric("Media Shared", num_media_messages)
        col4.metric("Links Shared", num_links)
        
        # Monthly Timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        if not timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.warning("No data available for the monthly timeline.")
        
        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        if not daily_timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.warning("No data available for the daily timeline.")
        
        # Activity Heatmap
        st.title("Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        if not user_heatmap.empty:
            fig, ax = plt.subplots()
            sns.heatmap(user_heatmap, cmap="coolwarm", annot=True, fmt="g")
            st.pyplot(fig)
        else:
            st.warning("No data available for the heatmap.")
        
        # Weekly Activity Map
        st.title("Weekly Activity Map")
        if not user_heatmap.empty:
            fig, ax = plt.subplots()
            sns.heatmap(user_heatmap)
            st.pyplot(fig)
        else:
            st.warning("No data available for weekly activity map.")
        
        # Busiest Users (for group analysis)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            if not x.empty:
                fig, ax = plt.subplots()
                col1, col2 = st.columns(2)
                with col1:
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)
            else:
                st.warning("No data available for most busy users.")
        
        # Word Cloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        if df_wc is not None:
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)
        else:
            st.warning("No data available for wordcloud.")
        
        # Most Common Words
        most_common_df = helper.most_common_words(selected_user, df)
        if not most_common_df.empty:
            fig, ax = plt.subplots()
            ax.barh(most_common_df['word'], most_common_df['count'])
            plt.xticks(rotation='vertical')
            st.title('Most Common Words')
            st.pyplot(fig)
        else:
            st.warning("No common words found.")
        
        # Emoji Analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")
        if not emoji_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df)
            
            with col2:
                fig, ax = plt.subplots()
                if os.path.exists(emoji_font_path):
                    emoji_font_prop = fm.FontProperties(fname=emoji_font_path, size=14)
                else:
                    emoji_font_prop = None
                    st.warning("Emoji font not found. Some emojis may not display correctly.")
                labels = [str(label) for label in emoji_df['emoji'].head()]
                wedges, texts, autotexts = ax.pie(emoji_df['count'].head(), labels=labels, autopct="%0.2f")
                if emoji_font_prop:
                    for text in texts + autotexts:
                        text.set_fontproperties(emoji_font_prop)
                    ax.set_title("Emoji Analysis", fontproperties=emoji_font_prop, fontsize=16)
                st.pyplot(fig)
        else:
            st.warning("No emoji data available.")