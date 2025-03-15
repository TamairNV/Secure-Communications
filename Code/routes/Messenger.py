from flask import Flask, render_template, redirect, url_for, request, session, Blueprint

from Code.Account import Account
from Code.routes.Chat import Chat, ChatMember
from Code.Password import Password
from Code.URLGenerator import URLGenerator


Messenger = Blueprint('Messenger', __name__)



@Messenger.route('/chat_creation', methods=['GET', 'POST'])
def chat_creation():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('verify_2fa'))

    if request.method == 'POST':
        # Handle actions (create or search)
        action = request.form.get('action')

        if action == 'create':
            chat_name = request.form.get('chat_name')  # Get chat name
            selected_friends = request.form.getlist('selected_friends')  # Get selected friends (list of IDs)

            Chat.createChat(chat_name, user_id)
            for friend in selected_friends:
                friend_id = int(friend)
                print(friend_id)
                Chat.addMember(user_id, chat_name, friend_id, 'member')

            return render_template('Messenger.html', user_chats=Chat.get_user_chats(user_id),
                                   user_requests=Account.get_all_friend_requests(user_id))

        elif action == 'search':
            search_query = request.form.get('search_friends').lower()  # Get search query
            query = """
                 SELECT friend.Friend_ID, Users.Username 
                 FROM SecureApp.friend 
                 JOIN SecureApp.Users ON friend.Friend_ID = Users.ID 
                 WHERE friend.User_ID = %s AND Users.Username LIKE %s;
             """
            filtered_friends = Account.executeQuery(query, [user_id, f"%{search_query}%"])
            # Re-render with filtered friends
            return render_template('chat_creation.html', friends=filtered_friends)
        else:
            # Fetch all friends for the user
            query = """
             SELECT friend.Friend_ID, Users.Username 
             FROM SecureApp.friend 
             JOIN SecureApp.Users ON friend.Friend_ID = Users.ID 
             WHERE friend.User_ID = %s;
             """
            friends = Account.executeQuery(query, [user_id])

    # Default rendering (GET request or unhandled POST)
    return render_template('chat_creation.html', friends=friends)


@Messenger.route('/friendRequestPage', methods=['GET', 'POST'])
def friendRequestPage():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('verify_2fa'))

    return render_template('friendRequestPage.html')



@Messenger.route('/messenger')
def messenger():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('verify_2fa'))

    # Fetch user chats and render the messenger page
    user_chats = Chat.get_user_chats(user_id)
    return render_template('friendRequestPage.html')



@Messenger.route('/accept_friend_request', methods=['POST'])
def accept_friend_request():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('verify_2fa'))

    friend_id = request.form.get('friend_id')
    print(friend_id)

    Account.add_friend(user_id, friend_id)
    return render_template('Messenger.html', user_chats=Chat.get_user_chats(user_id),
                           user_requests=Account.get_all_friend_requests(user_id))


@Messenger.route('/reject_friend_request', methods=['POST'])
def reject_friend_request():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('verify_2fa'))

    friend_id = request.form.get('friend_id')
    print(friend_id)
    Account.reject_request(user_id, friend_id)
    return render_template('Messenger.html', user_chats=Chat.get_user_chats(user_id),
                           user_requests=Account.get_all_friend_requests(user_id))


@Messenger.route('/search_query', methods=['GET', 'POST'])
def search_query():

    user_id = session.get('user_id')
    search_results = []
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        if search_query:
            query = "SELECT ID,Username FROM SecureApp.Users WHERE Username LIKE %s AND ID != %s"
            search_results = Account.executeQuery(query, [f"%{search_query}%", user_id])
    search_results = list(map(lambda x: x, search_results))
    print(search_results)
    return render_template('friendRequestPage.html', search_results=search_results)

@Messenger.route('/send_friend_request', methods=['GET', 'POST'])
def send_friend_request():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('verify_2fa'))
    Account.request_friend(user_id, request.form.get('friend_id'))
    return render_template('Messenger.html', user_chats=Chat.get_user_chats(user_id),
                           user_requests=Account.get_all_friend_requests(user_id))

@Messenger.route('/view_chat/<int:chat_id>')
def view_chat(chat_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('verify_2fa'))

    session['chat_id'] = chat_id


    return render_template('Messenger.html', user_chats=Chat.get_user_chats(user_id),
                           user_requests=Account.get_all_friend_requests(user_id),chat_messages = ChatMember.get_chat_messages(chat_id, user_id),selected_chat = chat_id)


@Messenger.route('/send_message',methods=['POST'])
def send_message():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('verify_2fa'))

    message_content = request.form.get('message')
    chat_id = session.get('chat_id')
    print(message_content,chat_id)
    ChatMember.sendMessage(chat_id,user_id,message_content)
    return render_template('Messenger.html', user_chats=Chat.get_user_chats(user_id),
                           user_requests=Account.get_all_friend_requests(user_id),chat_messages =  ChatMember.get_chat_messages(session.get('chat_id'),user_id))


