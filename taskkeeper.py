import streamlit as st
import requests

# class that makes api calls
class TaskKeeper:
    def __init__(self, base_url):
        self.base_url = base_url

# fetch data from api
    def fetch_tasks(self, cache_key=None):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()  # Raise an exception for bad responses
            return response.json()['tasks']
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching tasks: {e}")
            return None

# create new task, post request to api
    def create_task(self, title, description):
        try:
            data = {'title': title, 'description': description}
            response = requests.post(self.base_url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error creating task: {e}")
            return {}

# put request to api for update to task
    def update_task(self, task_id, title, description, completed):
        try:
            data = {'title': title, 'description': description, 'completed': completed}
            url = f'{self.base_url}/{task_id}'
            response = requests.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error updating task {task_id}: {e}")
            return {}

# delete request to api
    def delete_task(self, task_id):
        try:
            url = f'{self.base_url}/{task_id}'
            response = requests.delete(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error deleting task {task_id}: {e}")
            return {}

# run streamlit ui as part of class
    def run(self):
        st.set_page_config(layout="wide")
        st.markdown("<h1 style='text-align: center; '>Task Keeper</h1>", unsafe_allow_html=True)
        st.write("---")
        
        tasks = self.fetch_tasks()
        if tasks is None:
            st.error("Unable to connect to the API. Please check your connection.")
            if st.button('Refresh'):
                tasks = self.fetch_tasks()  # Retry fetching tasks on button click
        
        # streamlit columns 
        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])

        # add new task column
        with col1:
            st.header('Add new task')
            new_task_title = st.text_input('Title', key='new_task_title')
            new_task_description = st.text_area('Description', key='new_task_description')
            
            if st.button('Add'):
                result = self.create_task(new_task_title, new_task_description)
                if result:
                    st.success('Task added')
                    # invalidate cache by calling fetch_tasks with a different cache_key
                    self.fetch_tasks(new_task_title)  
                    
        # delete task column
        with col2:
            st.header('Delete task')
            delete_task_id = st.number_input('Enter Task ID', min_value=1, step=1, key='delete_task_id')
            if st.button('Delete Task'):
                result = self.delete_task(delete_task_id)
                if result:
                    st.success('Task deleted')
                    # invalidate cache by calling fetch_tasks with a different cache_key
                    self.fetch_tasks(delete_task_id)  

        # update task column
        with col3:
            st.header('Update task')
            tasks = self.fetch_tasks()
            task_options = {task['id']: f"ID: {task['id']} - {task['title']}" for task in tasks}
            selected_task_id = st.selectbox('Select task to update', list(task_options.keys()), key='selected_task_id')

            if selected_task_id:
                selected_task = next((task for task in tasks if task['id'] == selected_task_id), None)
                if selected_task:
                    st.text_input('Title', value=selected_task['title'], key='update_title')
                    st.text_area('Description', value=selected_task['description'], key='update_description')
                    st.checkbox('Completed', value=selected_task['completed'], key='update_completed')

                if st.button('Update task'):
                    result = self.update_task(selected_task_id, st.session_state.update_title, st.session_state.update_description, st.session_state.update_completed)
                    if result:
                        st.success('Task updated')
                        # invalidate cache by calling fetch_tasks with a different cache_key
                        self.fetch_tasks(selected_task_id)

        # table listing tasks
        with col4:
            st.header('Current tasks')
            tasks = self.fetch_tasks()
            if tasks:
                task_table = []
                for task in tasks:
                    task_status = "Yes" if task['completed'] else "No"
                    task_table.append({'ID': task['id'], 'Title': task['title'], 'Description': task['description'], 'Completed': task_status})
                st.table(task_table)
            else:
                st.write('No tasks available.')

        st.write("---")
        
# create instance of class and run
if __name__ == '__main__':
    BASE_URL = 'http://localhost:5000/api/tasks'
    task_manager = TaskKeeper(BASE_URL)
    task_manager.run()