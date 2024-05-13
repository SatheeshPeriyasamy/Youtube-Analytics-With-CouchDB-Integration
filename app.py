import streamlit as st
import requests
from couchdb import Server

couch = Server('http://admin:admin@localhost:5984/')
db = couch['testdb']


def fetch_youtube_data(channel_name):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        'part': 'snippet',
        'q': channel_name,
        'type': 'channel',
        'key': 'AIzaSyCqOcjtRAQZy2ahcpJ_epSPFrTC7RxqEPM'
    }
    search_resp = requests.get(search_url, params=search_params).json()
    channel_id = search_resp['items'][0]['id']['channelId']

    channel_url = "https://www.googleapis.com/youtube/v3/channels"
    channel_params = {
        'part': 'statistics',
        'id': channel_id,
        'key': 'your-api-key'
    }
    channel_resp = requests.get(channel_url, params=channel_params).json()
    return channel_resp['items'][0]


def save_to_couchdb(doc):
    return db.save(doc)

def get_all_docs():
    return [{'id': row.id, 'data': db[row.id]} for row in db.view('_all_docs', include_docs=True)]

def update_doc(doc_id, doc):
    doc['_rev'] = db[doc_id]['_rev']  
    db[doc_id] = doc
    return db[doc_id]

def delete_doc(doc_id):
    doc = db[doc_id]
    db.delete(doc)


st.title('YouTube Channel Analytics')

channel_name = st.text_input('Enter YouTube Channel Name:')
if st.button('Fetch Analytics'):
    channel_data = fetch_youtube_data(channel_name)
    doc_id, doc_rev = save_to_couchdb({
        'channel_name': channel_name,
        'channel_id': channel_data['id'],
        'analytics': channel_data['statistics']
    })
    st.success(f"Data saved with Doc ID: {doc_id}")

st.header('YouTube Analytics Records')
docs = get_all_docs()
doc_id_to_edit = st.selectbox('Select a record to view or edit:', [doc['id'] for doc in docs], index=0)

if doc_id_to_edit:
    doc_data = db[doc_id_to_edit]
    st.write('Data:', doc_data)

    new_channel_name = st.text_input("Edit Channel Name", value=doc_data['channel_name'])
    if st.button('Update Record'):
        doc_data['channel_name'] = new_channel_name
        update_doc(doc_id_to_edit, doc_data)
        st.success("Record updated!")

    if st.button('Delete Record'):
        delete_doc(doc_id_to_edit)
        st.success("Record deleted!")
