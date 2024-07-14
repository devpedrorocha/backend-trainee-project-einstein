import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Annotated, List
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import pandas as pd
import traceback
import tempfile
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Adicionar o middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos
    allow_headers=["*"],  # Permitir todos os headers
)


models.Base.metadata.create_all(bind=engine)

class UserBase(BaseModel):
    name: str
    role: str

class Report(BaseModel):
    id: str
    name: str
    date_test_carried_out: str

class GeneralQuestions(BaseModel):
    id: str
    report_id: str
    number_question: int
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

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    data: List[GeneralQuestions]
    total: int
    page: int
    size: int

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
async def create_report(reportName: str = Form(...), reportDate: str = '',correctFile: UploadFile = File(...), studentFile: UploadFile = File(...), db: Session = db_dependency):
    try:
        # Read XLSX files into pandas dataframes
        # with tempfile.NamedTemporaryFile(delete=False) as tmp_correct:
        #     tmp_correct.write(correctFile.file.read())
        #     correct_path = tmp_correct.name

        # with tempfile.NamedTemporaryFile(delete=False) as tmp_student:
        #     tmp_student.write(studentFile.file.read())
        #     student_path = tmp_student.name

        # correct_answers = pd.read_excel(correct_path)
        # student_answers = pd.read_excel(student_path)

        # Read the CSV files into pandas dataframes

        correct_answers = pd.read_csv(correctFile.file)
        student_answers = pd.read_csv(studentFile.file)

        id = str(uuid.uuid4())

        new_report = models.Reports(
            name=reportName,  
            id=id,
            date_test_carried_out=reportDate
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
            try:
                new_question = models.GeneralQuestions(
                    id=str(uuid.uuid4()),  # Generate a unique ID for each question
                    report_id=new_report.id,
                    number_question=coluna - 2,
                    content="Conteúdo",
                    # subject_id=disciplina,
                    correct_answer=gabaritoC,
                    difficulty_level="Easy",  # Adjust as necessary
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
                logging.info(f'Added new question: {new_question}')
                print(f'Questão:{coluna-2} Disciplina:{disciplina} Gabarito: {gabaritoC}\n A: {a}\n B: {b}\n C: {c}\n D: {d}\n E: {e} ')
                print(erraram, acertaram)
            except Exception as e:
                logging.error(f'Error adding new question: {e}')
                raise

           
        try:
            db.commit()  # Commit após adicionar todas as questões
            logging.info(f'Commit new question: {new_question}')

        except Exception as e:
                logging.error(f'Error adding Commit question: {e}')
                raise

        return JSONResponse(content={"message": "Report created successfully"}, status_code=201)
    except Exception as e:
        db.rollback()  # Reverte a transação em caso de erro
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()  # Fecha a sessão do banco de dados
    

@app.get('/reports', status_code=status.HTTP_200_OK, response_model=list[Report])
async def get_reports(db: Session = db_dependency):
    reports = db.query(models.Reports).all()
    return reports

@app.get('/reports/{report_id}', status_code=status.HTTP_200_OK, response_model=List[GeneralQuestions])
async def get_report(report_id: str, page: int = Query(1, ge=1), size: int = Query(10, ge=1), db: Session = Depends(get_db)):
    total = db.query(models.GeneralQuestions).filter(models.GeneralQuestions.report_id == report_id).all()
    
    
    if not total:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Relatório não encontrado')
    
    return total
