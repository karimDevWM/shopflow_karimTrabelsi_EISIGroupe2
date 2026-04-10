import pytest


@pytest.mark.integration
class TestProductsAvecFaker:
    def test_creation_donnees_faker(self, client, fake_product_data):
        """Crée un produit avec des données faker et vérifie la réponse."""
        response = client.post('/products/', json=fake_product_data)
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == fake_product_data['name']
        assert data['price'] == fake_product_data['price']

    def test_liste_avec_multiple_produits(self, client, multiple_products):
        """Vérifie que les 5 produits créés apparaissent dans la liste."""
        response = client.get('/products/')
        assert response.status_code == 200
        ids_liste = [p['id'] for p in response.json()]
        for p in multiple_products:
            assert p['id'] in ids_liste

    @pytest.mark.parametrize('prix,attendu_422', [
        (0.0, True),  # prix = 0 → invalide (gt=0)
        (-1.0, True),  # prix négatif → invalide
        (0.01, False),  # prix minimal valide
        (9999.99, False),  # prix élevé mais valide
    ])
    def test_validation_prix(self, client, prix, attendu_422):
        response = client.post(
            '/products/', json={'name': 'Test', 'price': prix, 'stock': 1})
        if attendu_422:
            assert response.status_code == 422
        else:
            assert response.status_code == 201

    # Q4.3 test_noms_longs() - (à faire)
    def test_noms_longs(self, client):
        """Un nom de 101 chars dépasse max_length=100 -> 422."""
        # 1) Nom trop long (101) -> 422
        nom_101 = "A" * 101
        response_long = client.post(
            "/products/",
            json={"name": nom_101, "price": 10.0, "stock": 1}
        )
        assert response_long.status_code == 422

        # 2) Vérifier que l'erreur concerne bien 'name' et la longueur max
        errors = response_long.json().get("detail", [])
        assert any(err.get("loc", [])[-1] == "name" for err in errors)
        assert any("at most 100" in err.get("msg", "").lower()
                   for err in errors)

        # 3) Nom limite (100) -> 201
        nom_100 = "B" * 100
        response_ok = client.post(
            "/products/",
            json={"name": nom_100, "price": 10.0, "stock": 1}
        )
        assert response_ok.status_code == 201
        assert response_ok.json()["name"] == nom_100
