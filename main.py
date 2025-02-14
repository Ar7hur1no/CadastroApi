from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv

# Carregar variaveis do ambiente
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("A variavel de ambiente DATABASE_URL nao foi definida")

# Configuracao do banco de dados
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos do banco de dados
class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=False)
    endereco = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    obrigacoes = relationship("ObrigacaoAcessoria", back_populates="empresa")

class ObrigacaoAcessoria(Base):
    __tablename__ = "obrigacoes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    periodicidade = Column(String, nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    empresa = relationship("Empresa", back_populates="obrigacoes")

# Schemas Pydantic
class EmpresaBase(BaseModel):
    nome: str
    cnpj: str
    endereco: str
    email: EmailStr
    telefone: str

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaResponse(EmpresaBase):
    id: int

    class Config:
        orm_mode = True

class ObrigacaoBase(BaseModel):
    nome: str
    periodicidade: str
    empresa_id: int

class ObrigacaoCreate(ObrigacaoBase):
    pass

class ObrigacaoResponse(ObrigacaoBase):
    id: int

    class Config:
        orm_mode = True

# Dependência de sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Criar a API
app = FastAPI()

# Endpoints CRUD para Empresas
@app.post("/empresas/", response_model=EmpresaResponse)
def create_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    db_empresa = Empresa(**empresa.dict())
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    return db_empresa

@app.get("/empresas/{empresa_id}", response_model=EmpresaResponse)
def get_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if empresa is None:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa

# Endpoints CRUD para Obrigações Acessórias
@app.post("/obrigacoes/", response_model=ObrigacaoResponse)
def create_obrigacao(obrigacao: ObrigacaoCreate, db: Session = Depends(get_db)):
    db_obrigacao = ObrigacaoAcessoria(**obrigacao.dict())
    db.add(db_obrigacao)
    db.commit()
    db.refresh(db_obrigacao)
    return db_obrigacao

@app.get("/obrigacoes/{obrigacao_id}", response_model=ObrigacaoResponse)
def get_obrigacao(obrigacao_id: int, db: Session = Depends(get_db)):
    obrigacao = db.query(ObrigacaoAcessoria).filter(ObrigacaoAcessoria.id == obrigacao_id).first()
    if obrigacao is None:
        raise HTTPException(status_code=404, detail="Obrigação não encontrada")
    return obrigacao

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)
