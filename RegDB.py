


import sqlite3
import hashlib
import datetime

DB_PATH = 'db/slc_reg.db'


class RegDB:

    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        return

    def pass_hash(self, text):
        return hashlib.md5(text.encode()).hexdigest()[:9]

    def confirm_login(self, username, password):
        c = self.db.cursor()
        c.execute('SELECT COUNT(*) FROM _Users WHERE username = ? AND password = ?;', (username, self.pass_hash(password)))
        return c.fetchone()[0] > 0

    def user_already_exists(self, username):
        c = self.db.cursor()
        c.execute("SELECT COUNT(*) FROM _Users WHERE username = ?;", (username,))
        return c.fetchone()[0] > 0

    def get_new_uid(self):
        c = self.db.cursor()
        c.execute('SELECT MAX(user_id) FROM _Users;')
        last_max = c.fetchone()[0]
        if last_max is None:
            return 0
        else:
            return last_max + 1

    def add_user(self, username, password):
        assert not self.user_already_exists(username), "ERROR! Username already exists: " + username
        c = self.db.cursor()
        c.execute('INSERT INTO _Users (user_id, username, password) VALUES (?, ?, ?);', (self.get_new_uid(), username, self.pass_hash(password)))
        self.db.commit()
        return

    def pull_courses(self, form_response):
        # Pull out data
        query = 'SELECT course, course_title, instructor, term, course_type FROM CourseInfo WHERE'
        vals = tuple()
        if form_response['keyword'] != '':
            if len(vals) > 0: query += ' AND'
            query += ' course_title LIKE ?'
            vals += ('%' + form_response['keyword'] + '%',)
        if form_response['instructor'] != '':
            if len(vals) > 0: query += ' AND'
            query += ' instructor LIKE ?'
            vals += ('%' + form_response['instructor'] + '%',)
        if form_response['term'] != 'all':
            if len(vals) > 0: query += ' AND'
            query += ' term LIKE ?'
            vals += ('%' + form_response['term'] + '%',)
        if form_response['coursetype'] != 'all':
            if len(vals) > 0: query += ' AND'
            query += ' course_type LIKE ?'
            vals += ('%' + form_response['coursetype'] + '%',)
        if form_response['department'] != 'all':
            if len(vals) > 0: query += ' AND'
            query += ' department LIKE ?'
            vals += ('%' + form_response['department'] + '%',)
        if len(vals) == 0:
            return None
        else:
            c = self.db.cursor()
            print(query, vals)
            c.execute(query, vals)
            return c.fetchall()

    def get_course_info(self, course_id):
        query = 'SELECT course, course_title, instructor, term, course_type FROM CourseInfo WHERE course = ?'
        c = self.db.cursor()
        c.execute(query, (course_id,))
        return c.fetchall()

    def get_course_name(self, course_id):
        query = 'SELECT course, course_title FROM CourseInfo WHERE course = ?'
        c = self.db.cursor()
        c.execute(query, (course_id,))
        return c.fetchone()[1]

    def get_name_and_times(self, course_id):
        query = 'SELECT course, day_index, start_time, end_time, term  FROM MeetingTimes NATURAL JOIN CourseInfo WHERE course = ?'
        c = self.db.cursor()
        c.execute(query, (course_id,))
        course_list = [list(course) for course in c]
        for i, course in enumerate(course_list):
            course_list[i].append(self.get_course_name(course[0]))
        course_list
        return course_list

    def create_course_dict(self, course_id):
        return [dict(zip(['course_id', 'day', 'start_time', 'end_time', 'term', 'course_title'], meeting)) for meeting in self.get_name_and_times(course_id)]

    def list_of_course_dicts(self, course_ids):
        """
        NOTE: Currently returns a list of lists, where each unique course has it's own list. 
        Should it return one list of course objects instead?
        """
        return [self.create_course_dict(cid) for cid in course_ids]

    def do_meetings_conflict(self, c1, c2, start_end_conflict=False):
        """
        Returns 'True' if c1 and c2 conflict.

        Only non-conflicts are:
            – c1 starts and ends* before c2 starts
            – or c2 starts and ends* before c1 starts
        
        * 'start_end_conflict' (default is False) If 'True', c1 ending at the same time as c2 starts IS a conflict.
        """
        # Extract times
        c1_term  = c1['term']
        c2_term  = c2['term']

        c1_day   = c1['day']
        c2_day   = c2['day']

        c1_start = c1['start_time']
        c1_end   = c1['end_time']

        c2_start = c2['start_time']
        c2_end   = c2['end_time']
        # Check for conflicts
        # Make sure they both have term / day / times
        if '' in [c1_term, c2_term, c1_day, c2_day]:
            return True
        for t in [c1_start, c2_start, c1_end, c2_end]:
            if not isinstance(t, int):
                return True
        # Are they during the same semester?
        if (c1_term == 'Fall' and c2_term == 'Spring') or (c1_term == 'Fall' and c2_term == 'Spring'):
            return False
        else:
            # Do they meet on the same day?
            if c1_day != c2_day:
                return False
            else:
                # Do they meet at the same time?
                if c1_start < c2_start and (c1_end < c2_start or (not start_end_conflict and c1_end == c2_start)):
                    # c1 starts and ends* before c2 starts
                    return False
                elif c2_end < c1_start or (not start_end_conflict and c2_end == c1_start):
                    # c2 starts and ends* before c1 starts
                    return False
                else: # Otherwise, it's a conflict
                    return True

    def check_for_conflicts(self, course_dict_list):
        """
        Checks for conflicts between a 'schedule' of 3 courses.
        Returns 'True' if schedule is good or 'False' if there is a conflict.

        Assumes a list of lists of dicts – where first list is length 3 (one for each course).
        Subsequent lists are lists of meeting times for each class.
        Dicts represent a course meeting time.
        """
        assert len(course_dict_list) == 3, "'course_dict_list' should be length = 3"

        c1, c2, c3 = course_dict_list
        for m1 in c1:
            for m2 in c2:
                if self.do_meetings_conflict(m1, m2):
                    return False
        for m1 in c2:
            for m2 in c3:
                if self.do_meetings_conflict(m1, m2):
                    return False
        for m1 in c1:
            for m2 in c3:
                if self.do_meetings_conflict(m1, m2):
                    return False
        return True

    def cart_to_schedules(self, cart):
        """ 
        Takes a list of course_id s and returns a comprehensive list of 
        possible schedules where courses don't conflict.
        """
        assert isinstance(cart, list), 'ERROR! Cart should be a list'
        assert [type(x) for x in cart].count(str) == len(cart), 'ERROR! All values in cart should be strings!'

        # Make a list of all possible permutations
        id_schedules = []
        for c1 in cart:
            for c2 in cart:
                for c3 in cart:
                    if c1 == c2 or c2 == c3 or c1 == c3: continue
                    schedule_candidate = {c1, c2 ,c3}
                    if schedule_candidate in id_schedules: continue
                    id_schedules.append(schedule_candidate)
        # Turn the sets into lists
        id_schedules = [list(s) for s in id_schedules]
        # Turn them into dict_objects and check for conflicts
        good_schedules = []
        for s in id_schedules:
            dict_schedule = self.list_of_course_dicts(s)
            if self.check_for_conflicts(dict_schedule):
                good_schedules.append(dict_schedule)
        return good_schedules

    def get_cart_conflicts(self, cart):
        conflicts = []
        course_dict_list = self.list_of_course_dicts(cart)
        for i, c1 in enumerate(course_dict_list[:-1]):
            for c2 in course_dict_list[i+1:]:
                for c1m in c1:
                    for c2m in c2:
                        if self.do_meetings_conflict(c1m, c2m):
                            if '' in [c1m['term'], c2m['term'], c1m['day'], c2m['day']]:
                                continue
                            if [type(t) for t in [c1m['start_time'], c2m['start_time'], c1m['end_time'], c2m['end_time']]].count(int) < 4:
                                continue
                            conflicts.append((c1m, c2m))
        return conflicts

    def format_time(self, time):
        hour = time // 100
        minute = time % 100
        dt = datetime.time(hour, minute)
        return dt.strftime('%I:%M %p')

    def formatted_conflicts(self, cart):
        raw_conflicts = self.get_cart_conflicts(cart)
        if len(raw_conflicts) < 1:
            return None
        conflict_list = []
        for c1m, c2m in raw_conflicts:
            try:
                conflict_list.append((
                    c1m['course_id'] + ': ' + c1m['course_title'],
                    c2m['course_id'] + ': ' + c2m['course_title'],
                    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][c1m['day']],
                    self.format_time(c1m['start_time']) + ' – ' + self.format_time(c1m['end_time']),
                    self.format_time(c2m['start_time']) + ' – ' + self.format_time(c2m['end_time'])
                ))
            except:
                pass
        return conflict_list


    def get_cart(self, username):
        c = self.db.cursor()
        c.execute('SELECT course FROM Carts WHERE user_id = ?;', (username,))
        cart = [course[0] for course in c]
        if cart is not None:
            return cart
        else:
            return None

    def add_class_to_cart(self, username, course_id):
        c = self.db.cursor()
        try:
            c.execute('INSERT INTO Carts (user_id, course) VALUES (?, ?);', (username, course_id))
        except sqlite3.DatabaseError as e:
            if 'unique' in str(e).lower():
                print(e)
                pass
            else:
                raise e
        self.db.commit()
        return

    def del_class_from_cart(self, username, course_id):
        c = self.db.cursor()
        c.execute('DELETE FROM Carts WHERE user_id = ? AND course = ?;', (username, course_id))
        self.db.commit()
        return


if __name__ == '__main__':
    rdb = RegDB()