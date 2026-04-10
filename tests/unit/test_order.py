import pytest
from app.models import Product, Cart, CartItem, Coupon, Order
from app.services.order import creer_commande, mettre_a_jour_statut
from app.services.cart import get_or_create_cart


@pytest.mark.unit
class TestOrderService:
    def test_creer_commande_panier_vide(self, db_session):
        cart = get_or_create_cart(1, db_session)
        with pytest.raises(ValueError, match="panier vide"):
            creer_commande(1, cart, db_session)

    def test_creer_commande_sans_coupon(self, db_session, mocker):
        mocker.patch("app.services.stock.redis_client")
        p = Product(name="A", price=50.0, stock=10)
        db_session.add(p)
        db_session.commit()
        db_session.refresh(p)

        cart = get_or_create_cart(1, db_session)
        db_session.add(CartItem(cart_id=cart.id, product_id=p.id, quantity=2))
        db_session.commit()
        db_session.refresh(cart)

        order = creer_commande(1, cart, db_session)

        assert order.user_id == 1
        assert order.total_ht == 100.0
        assert order.total_ttc == 120.0
        assert order.coupon_code is None
        assert order.status == "pending"

        db_session.refresh(p)
        assert p.stock == 8
        db_session.refresh(cart)
        assert len(cart.items) == 0

    def test_creer_commande_avec_coupon(self, db_session, mocker):
        mocker.patch("app.services.stock.redis_client")
        p = Product(name="A", price=100.0, stock=10)
        c = Coupon(code="PROMO20", reduction=20.0, actif=True)
        db_session.add_all([p, c])
        db_session.commit()
        db_session.refresh(p)

        cart = get_or_create_cart(1, db_session)
        db_session.add(CartItem(cart_id=cart.id, product_id=p.id, quantity=1))
        db_session.commit()
        db_session.refresh(cart)

        order = creer_commande(1, cart, db_session, c)

        assert order.total_ht == 100.0
        assert order.total_ttc == 96.0  # TTC 120 puis -20%
        assert order.coupon_code == "PROMO20"

    def test_mettre_a_jour_statut_commande_introuvable(self, db_session):
        with pytest.raises(ValueError, match="non trouvée"):
            mettre_a_jour_statut(999, "confirmed", db_session)

    def test_mettre_a_jour_statut_transition_invalide(self, db_session):
        o = Order(user_id=1, total_ht=10.0, total_ttc=12.0, status="pending")
        db_session.add(o)
        db_session.commit()
        db_session.refresh(o)

        with pytest.raises(ValueError, match="Transition invalide"):
            mettre_a_jour_statut(o.id, "shipped", db_session)

    def test_mettre_a_jour_statut_valide(self, db_session):
        o = Order(user_id=1, total_ht=10.0, total_ttc=12.0, status="pending")
        db_session.add(o)
        db_session.commit()
        db_session.refresh(o)

        updated = mettre_a_jour_statut(o.id, "confirmed", db_session)
        assert updated.status == "confirmed"
