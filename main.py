import uuid
from fastapi import FastAPI, UploadFile, File,HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import pandas as pd
import traceback
import tempfile
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://localhost",
    "http://localhost:3000",  # Adjust this if your frontend runs on a different port
    "http://127.0.0.1",
    "http://127.0.0.1:3000",  # Adjust this if your frontend runs on a different port
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


models.Base.metadata.create_all(bind=engine)

class UserBase(BaseModel):
    name: str
    role: str

class Report(BaseModel):
    name: str
    date_test_executed: str

class GeneralQuestions(BaseModel):
    report_id: str
    class_id: str
    subject_id: str
    content: str
    correct_answer: str
    difficulty_level: str
    analysis_description: str
    selected_correct_answer_quantity: int
    selected_wrong_answer_quantity: int
    selected_letter_a_quantity: int
    selected_letter_b_quantity: int
    selected_letter_c_quantity: int
    selected_letter_d_quantity: int
    selected_letter_e_quantity: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Correct usage of Annotated without setting it as response model
db_dependency = Depends(get_db)

@app.post('/users/', status_code=status.HTTP_201_CREATED, response_model=UserBase)
async def create_user(user: UserBase, db: Session = db_dependency):
    new_user = models.Users(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get('/users/{user.id}', status_code=status.HTTP_200_OK, response_model=UserBase)
async def get_user(user_id: int, db: Session = db_dependency):
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuário não encontrado')
    return user


@app.post('/reports/', status_code=status.HTTP_201_CREATED, response_model=Report)
async def create_report(correctFile: UploadFile = File(...), studentFile: UploadFile = File(...), db: Session = db_dependency):
    try:
        # Read the CSV files into pandas dataframes
        # with tempfile.NamedTemporaryFile(delete=False) as tmp_correct:
        #     tmp_correct.write(correctFile.file.read())
        #     correct_path = tmp_correct.name

        # with tempfile.NamedTemporaryFile(delete=False) as tmp_student:
        #     tmp_student.write(studentFile.file.read())
        #     student_path = tmp_student.name

        # correct_answers = pd.read_excel(correct_path)
        # student_answers = pd.read_excel(student_path)
        correct_answers = pd.read_csv(correctFile.file)
        student_answers = pd.read_csv(studentFile.file)
        print(correct_answers)
        print(student_answers)

        id = uuid.uuid4()

        new_report = Report(
            name="Report Name",  
            id_class=id,
            date_test_carried_out="2024-06-10" 
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)  # Refresh to get the ID of the newly created report

        n_linhas = student_answers.shape[0]
        n_colunas = student_answers.shape[1]


        for coluna in range(3, 53):
            a = b = c = d = e = acertaram = erraram = 0
         
            for linha in range(n_linhas - 1):
                colunaG = coluna - 3
                disciplina = student_answers.iloc[0, coluna]
                gabaritoC = correct_answers.iloc[colunaG, 0]
                resposta_aluno = student_answers.iloc[linha, coluna]
                if resposta_aluno == 'NAO DETECTADO':
                    continue
                if resposta_aluno == "A":
                    a += 1
                elif resposta_aluno == "B":
                    b += 1
                elif resposta_aluno == "C":
                    c += 1
                elif resposta_aluno == 'D':
                    d += 1
                elif resposta_aluno == "E":
                    e += 1
                if resposta_aluno == gabaritoC:
                    acertaram += 1
                else:
                    erraram += 1

            total_respostas = acertaram + erraram
            if total_respostas > 0:
                acertaram_percent = (acertaram / total_respostas) * 100
                erraram_percent = (erraram / total_respostas) * 100
            else:
                acertaram_percent = erraram_percent = 0

            # Create a new GeneralQuestions object
            new_question = GeneralQuestions(
                report_id=new_report.id,
                content=f"Question {coluna - 2}",
                correct_answer=gabaritoC,
                difficulty_level="Easy",  # Adjust this as needed
                analysis_description="",
                selected_correct_answer_quantity=acertaram,
                selected_wrong_answer_quantity=erraram,
                selected_letter_a_quantity=a,
                selected_letter_b_quantity=b,
                selected_letter_c_quantity=c,
                selected_letter_d_quantity=d,
                selected_letter_e_quantity=e
            )
            db.add(new_question)
            
            print(f'Questão:{coluna-2} Disciplina:{disciplina} Gabarito: {gabaritoC}\n A: {a}\n B: {b}\n C: {c}\n D: {d}\n E: {e} ')
            print(erraram, acertaram)
            db
        # Return a response (you can customize the response as needed)
        return JSONResponse(content={"message": "Report created successfully"}, status_code=201)
    
    except Exception as e:
        print(f'Error occurred: {e}')
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/reports/{report.id}', status_code=status.HTTP_200_OK, response_model=Report)
async def get_report(report_id: int, db: Session = db_dependency):
    report = db.query(models.Reports).filter(models.Reports.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Relatório não encontrado')
    return report
