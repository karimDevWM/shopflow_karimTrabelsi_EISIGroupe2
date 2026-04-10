from faker import Faker
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Product, Coupon


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def product_sample(db_session):
    p = Product(name="Laptop Pro", price=999.99, stock=10)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def coupon_sample(db_session):
    c = Coupon(code="PROMO20", reduction=20.0, actif=True)
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture(scope="function")
def client(db_engine, monkeypatch):
    # Important: patch AVANT les requêtes
    monkeypatch.setattr("app.routes.products.get_cached",
                        lambda key: None)
    monkeypatch.setattr("app.routes.products.set_cached",
                        lambda *args, **kwargs: None)
    monkeypatch.setattr("app.routes.products.delete_cached",
                        lambda *args, **kwargs: None)

    SessionTest = sessionmaker(bind=db_engine)

    def override_get_db():
        session = SessionTest()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def api_product(client):
    response = client.post("/products/", json={
        "name": "Clavier Mécanique",
        "price": 89.99,
        "stock": 25,
        "category": "peripheriques",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def api_coupon(client):
    response = client.post("/coupons/", json={
        "code": "PROMO10",
        "reduction": 10.0,
        "actif": True,
    })
    assert response.status_code == 201
    return response.json()


fake = Faker('fr_FR')  # données en français


@pytest.fixture
def fake_product_data():
    """Génère un payload produit réaliste et aléatoire."""
    return {
        'name': fake.catch_phrase()[:50],  # ex: 'Synergistic Rubber Chair'
        'price': round(fake.pyfloat(min_value=1, max_value=2000, right_digits=2), 2),
        'stock': fake.random_int(min=0, max=500),
        'category': fake.random_element(['informatique', 'peripheriques', 'audio', 'gaming']),
        'description': fake.sentence(nb_words=10),
    }


@pytest.fixture
def multiple_products(client):
    """Crée 5 produits avec faker pour tester la liste et les filtres."""
    faker_inst = Faker()
    products = []
    for i in range(5):
        r = client.post('/products/', json={
            'name': faker_inst.word().capitalize() + f' {i}',
            'price': round(10.0 + i * 20, 2),
            'stock': 10,
        })
        products.append(r.json())
    yield products
# Cleanup : désactiver les 5 produits
    for p in products:
        client.delete(f'/products/{p["id"]}')
