import pytest


@pytest.mark.integration
class TestListProducts:
    def test_liste_vide_au_demarrage(self, client):
        """Sans données, GET /products/ retourne une liste vide."""
        response = client.get('/products/')
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_produit_cree_apparait_dans_liste(self, client, api_product):
        response = client.get('/products/')
        assert response.status_code == 200
        ids = [p['id'] for p in response.json()]
        assert api_product['id'] in ids

    def test_filtre_par_categorie(self, client):
        # Créer un produit avec catégorie spécifique
        client.post('/products/', json={
            'name': 'GPU RTX', 'price': 799.0, 'stock': 3, 'category': 'gpu'
        })
        response = client.get('/products/?category=gpu')
        assert response.status_code == 200
        for p in response.json():
            assert p['category'] == 'gpu'

    def test_pagination_limit(self, client):
        for i in range(5):
            client.post(
                '/products/', json={'name': f'Prod{i}', 'price': 10.0, 'stock': 1})
            response = client.get('/products/?limit=2')
            assert response.status_code == 200
            assert len(response.json()) <= 2

    def test_pagination_skip(self, client):
        """skip=1000 → liste vide ou résultats après le 1000e."""
        response = client.get('/products/?skip=1000&limit=10')
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.integration
class TestGetProduct:
    def test_get_produit_existant(self, client, api_product):
        pid = api_product['id']
        response = client.get(f'/products/{pid}')
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == pid
        assert data['name'] == api_product['name']


def test_get_produit_inexistant_retourne_404(client):
    response = client.get('/products/99999')
    assert response.status_code == 404


def test_schema_complet(client, api_product):
    response = client.get(f'/products/{api_product["id"]}')
    data = response.json()
    for field in ["id", "name", "price", "stock", "active", "created_at"]:
        assert field in data
