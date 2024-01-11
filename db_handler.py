import psycopg2
import bcrypt
from datetime import datetime

def connect_db():
    return psycopg2.connect(
        dbname='',
        user='',
        password='',
        host='',
        port=''
    )

def add_user(nickname, password):
    conn = connect_db()
    cur = conn.cursor()
    
    pwhash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_pass = pwhash.decode('utf-8')
    sql = """
        INSERT INTO users (nickname, password, created_at)
        VALUES (%s,%s,%s)
    """
    current_time = datetime.now()

    cur.execute(sql, (nickname, hashed_pass, current_time))
    conn.commit()
    cur.close()
    conn.close()

def is_username_exists(nickname):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE nickname = %s", (nickname,))
    exists = bool(cur.rowcount)
    cur.close()
    conn.close()
    return exists

def verify_login(nickname,password):
    conn = connect_db()
    curr = conn.cursor()
    curr.execute("SELECT password FROM users WHERE nickname = %s", (nickname,))
    check_password = curr.fetchone()
    print(check_password)
    if check_password :
        hashed_pass = check_password[0].encode('utf-8')
        entered_pass = bcrypt.hashpw(password.encode('utf-8'), hashed_pass)

        if hashed_pass == entered_pass:
            return True
    return False

def get_id(nickname):
    conn = connect_db()  
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE nickname = %s", (nickname,))
        user_data = cursor.fetchone()
        print('Query result: ', user_data)
        if user_data:
            user_id = user_data[0]
        else:
            user_id = None  
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error fetching user ID from database:", error)
        user_id = None
    finally:
        cursor.close()
        conn.close()

    return user_id

def get_random_question():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, question_text, first_choice, second_choice, third_choice, fourth_choice FROM quiz ORDER BY RANDOM() LIMIT 1")
    question = cursor.fetchone()
    
    cursor.close()
    conn.close()

    return {
        'id': question[0],
        'question_text': question[1],
        'first_choice': question[2],
        'second_choice': question[3],
        'third_choice': question[4],
        'fourth_choice': question[5]
    }


def get_correct_answer(question_id):
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT correct_answer FROM quiz WHERE id = %s", (question_id,))
    correct_answer = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return correct_answer


def update_leaderboard(user_id, score_change):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        print("Updating leaderboard for user:", user_id)
        sql = """
            INSERT INTO leaderboard (user_id, score)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET score = leaderboard.score + %s;
        """
        cursor.execute(sql, (user_id, score_change, score_change))

        conn.commit()
        return True  
    except Exception as e:
        print("Error updating leaderboard:", e)
        return False  
    finally:
        cursor.close()
        conn.close()

def get_score (user_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT score FROM leaderboard WHERE user_id = %s", (user_id,))
        user_score = cursor.fetchone()
        if user_score:
            return user_score[0]
        else:
            return None  
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error fetching user score:", error)
        return None  
    finally:
        cursor.close()
        conn.close()

def get_leaderboard_data():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT users.id as user_id, users.nickname as nickname, COALESCE(SUM(leaderboard.score), 0) as total_score
            FROM users
            LEFT JOIN leaderboard ON users.id = leaderboard.user_id
            GROUP BY users.id, users.nickname
            ORDER BY total_score DESC
        """)
        leaderboard_data = cursor.fetchall()

        users = [{'user_id': row[0], 'nickname': row[1], 'total_score': row[2]} for row in leaderboard_data]

        return users
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error fetching leaderboard data:", error)
        return []
    finally:
        cursor.close()
        conn.close()

