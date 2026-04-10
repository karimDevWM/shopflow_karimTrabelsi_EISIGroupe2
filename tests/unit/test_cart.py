import pytest
from app.models import Product, Cart, CartItem
from app.services.cart import (
    get_or_create_cart, ajouter_au_panier, retirer_du_panier, vider_panier,
    calculer_sous_total, calculer_total_ttc
)


@pytest.mark.unit
class TestCartService:
    def test_get_or_create_cart_cree(self, db_session):
        cart = get_or_create_cart(1, db_session)
        assert cart.user_id == 1
        assert cart.id is not None

    def test_get_or_create_cart_existant(self, db_session):
        c1 = get_or_create_cart(1, db_session)
        c2 = get_or_create_cart(1, db_session)
        assert c1.id == c2.id

    def test_ajouter_au_panier_quantite_invalide(self, product_sample, db_session):
        with pytest.raises(ValueError, match="invalide"):
            ajouter_au_panier(product_sample, 0, 1, db_session)

    def test_ajouter_au_panier_stock_insuffisant(self, product_sample, db_session):
        with pytest.raises(ValueError, match="insuffisant"):
            ajouter_au_panier(product_sample, 999, 1, db_session)

    def test_ajouter_au_panier_nouvel_item(self, product_sample, db_session):
        cart = ajouter_au_panier(product_sample, 2, 1, db_session)
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 2

    def test_ajouter_au_panier_item_existant_increment(self, product_sample, db_session):
        ajouter_au_panier(product_sample, 2, 1, db_session)
        cart = ajouter_au_panier(product_sample, 3, 1, db_session)
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 5

    def test_retirer_du_panier_ok(self, product_sample, db_session):
        cart = ajouter_au_panier(product_sample, 1, 1, db_session)
        cart = retirer_du_panier(cart, product_sample.id, db_session)
        assert len(cart.items) == 0

    def test_retirer_du_panier_introuvable(self, db_session):
        cart = get_or_create_cart(1, db_session)
        with pytest.raises(ValueError, match="non trouvé"):
            retirer_du_panier(cart, 999, db_session)

    def test_vider_panier(self, product_sample, db_session):
        cart = ajouter_au_panier(product_sample, 2, 1, db_session)
        cart = vider_panier(cart, db_session)
        assert len(cart.items) == 0

    def test_calculer_sous_total_vide(self, db_session):
        cart = get_or_create_cart(1, db_session)
        assert calculer_sous_total(cart) == 0.0

    def test_calculer_sous_total_et_ttc(self, db_session):
        p1 = Product(name="A", price=10.0, stock=10)
        p2 = Product(name="B", price=20.0, stock=10)
        db_session.add_all([p1, p2])
        db_session.commit()
        cart = get_or_create_cart(1, db_session)
        db_session.add_all([
            CartItem(cart_id=cart.id, product_id=p1.id, quantity=2),
            CartItem(cart_id=cart.id, product_id=p2.id, quantity=1),
        ])
        db_session.commit()
        db_session.refresh(cart)

        assert calculer_sous_total(cart) == 40.0
        assert calculer_total_ttc(cart) == 48.0
