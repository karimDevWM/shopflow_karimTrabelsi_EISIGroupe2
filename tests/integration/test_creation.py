import pytest


@pytest.mark.integration
class TestCreateProduct:
    def test_creation_valide(self, client):
        payload = {'name': 'Souris Ergonomique', 'price': 49.99, 'stock': 30}
        response = client.post('/products/', json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'Souris Ergonomique'
        assert data['price'] == 49.99
        assert data['id'] is not None

    def test_creation_prix_negatif_422(self, client):
        response = client.post(
            '/products/', json={'name': 'X', 'price': -10.0, 'stock': 5})
        assert response.status_code == 422

    def test_creation_nom_vide_422(self, client):
        response = client.post(
            '/products/', json={'name': '', 'price': 10.0, 'stock': 5})
        assert response.status_code == 422

    def test_creation_stock_negatif_422(self, client):
        response = client.post(
            '/products/', json={'name': 'T', 'price': 10.0, 'stock': -1})
        assert response.status_code == 422

    def test_active_true_par_defaut(self, client):
        response = client.post(
            '/products/', json={'name': 'Actif', 'price': 1.0, 'stock': 1})
        assert response.json()['active'] is True


@pytest.mark.integration
class TestUpdateDeleteProduct:
    def test_mise_a_jour_prix(self, client, api_product):
        pid = api_product['id']
        response = client.put(f'/products/{pid}', json={'price': 79.99})
        assert response.status_code == 200
        assert response.json()['price'] == 79.99

    def test_mise_a_jour_stock(self, client, api_product):
        pid = api_product['id']
        response = client.put(f'/products/{pid}', json={'stock': 100})
        assert response.status_code == 200
        assert response.json()['stock'] == 100

    def test_suppression_soft_delete(self, client):
        """DELETE désactive le produit (soft delete) — il n'est plus accessible."""
        create = client.post(
            '/products/', json={'name': 'A supprimer', 'price': 1.0, 'stock': 1})
        pid = create.json()['id']
        response = client.delete(f'/products/{pid}')
        assert response.status_code == 204
        # Vérifier que le produit n'est plus accessible
        get_resp = client.get(f'/products/{pid}')
        assert get_resp.status_code == 404
        # test_filtre_prix_min_max() reponse Q2.4 (à faire)

    def test_filtre_prix_min_max(self, client):
        """GET /products/?min_price=50&max_price=200 retourne seulement les produits
        dont le prix est entre 50€ et 200€ inclus."""
        # Créer 3 produits avec des prix différents
        r1 = client.post(
            "/products/", json={"name": "Trop bas", "price": 20.0, "stock": 5})
        r2 = client.post(
            "/products/", json={"name": "Dans la fourchette", "price": 100.0, "stock": 5})
        r3 = client.post(
            "/products/", json={"name": "Trop haut", "price": 300.0, "stock": 5})
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r3.status_code == 201

        # Filtrer : min=50, max=200
        response = client.get("/products/?min_price=50&max_price=200")
        assert response.status_code == 200
        data = response.json()

        # Vérifier que tous les résultats sont dans la fourchette
        assert all(50 <= p["price"] <= 200 for p in data)

        # Vérifier présence/absence attendues
        names = {p["name"] for p in data}
        assert "Dans la fourchette" in names
        assert "Trop bas" not in names
        assert "Trop haut" not in names

    def test_filtre_prix_min_max(self, client):
        """GET /products/?min_price=50&max_price=200 retourne uniquement les produits dans [50, 200]."""
        # 1) Créer 3 produits: un en dessous, un dans la plage, un au-dessus
        r1 = client.post(
            "/products/", json={"name": "Trop bas", "price": 20.0, "stock": 5})
        r2 = client.post(
            "/products/", json={"name": "Dans la fourchette", "price": 100.0, "stock": 5})
        r3 = client.post(
            "/products/", json={"name": "Trop haut", "price": 300.0, "stock": 5})
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r3.status_code == 201

        # 2) Appliquer le filtre min/max
        response = client.get("/products/?min_price=50&max_price=200")
        assert response.status_code == 200
        data = response.json()

        # 3) Vérifier que tous les prix sont dans la fourchette
        assert all(50 <= p["price"] <= 200 for p in data)

        # 4) Vérifier présence/absence des produits attendus
        names = {p["name"] for p in data}
        assert "Dans la fourchette" in names
        assert "Trop bas" not in names
        assert "Trop haut" not in names
