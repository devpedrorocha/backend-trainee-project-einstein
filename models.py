from sqlalchemy import Boolean, Column, ForeignKey , Integer, String
from database import Base


class Users(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=False)
    role = Column(String(50), unique=False)


class Subjects(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    report = Column(Integer, ForeignKey('reports.id'))

class Reports(Base):
    __tablename__ = 'reports'

    id = Column(String, primary_key=True, index=True)
    name = Column(String(50), unique=False)
    id_class = Column(Integer, ForeignKey('classes.id'))
    date_test_carried_out = Column(String(50), unique=False)

class Classes(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=False)
    report_id = Column(Integer, ForeignKey('reports.id'))
    

class GeneralQuestions(Base):
    __tablename__ = 'general_questions'

    id = Column(String, primary_key=True, index=True)
    report_id = Column(String, ForeignKey('reports.id'))
    class_id = Column(String, ForeignKey('classes.id'))
    subject_id = Column(String, ForeignKey('subjects.id'))
    content = Column(String(50), unique=False)
    correct_answer = Column(String(2), unique=False)
    difficulty_level = Column(String(15), unique=False)

    analysis_description = Column(String(500), unique=False)
    selected_correct_answer_quantity = Column(Integer, unique=False)
    selected_wrong_answer_quantity = Column(Integer, unique=False)

    selected_letter_a_quantity = Column(Integer, unique=False)
    selected_letter_b_quantity = Column(Integer, unique=False)
    selected_letter_c_quantity = Column(Integer, unique=False)
    selected_letter_d_quantity = Column(Integer, unique=False)
    selected_letter_e_quantity = Column(Integer, unique=False)