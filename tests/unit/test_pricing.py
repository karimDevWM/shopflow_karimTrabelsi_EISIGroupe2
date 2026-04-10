# tests/unit/test_pricing.py
from app.models import Coupon, Product
import pytest
from app.services.pricing import calcul_prix_ttc, appliquer_coupon, calculer_total, calculer_remise

# ── TESTS calcul_prix_ttc ──────────────────────────────────────


@pytest.mark.unit
class TestCalculPrixTtc:
    def test_prix_normal(self):
        """Prix HT 100€ → TTC 120€ avec TVA 20%."""
        assert calcul_prix_ttc(100.0) == 120.0

    def test_prix_zero(self):
        assert calcul_prix_ttc(0.0) == 0.0

    def test_arrondi_deux_decimales(self):
        assert calcul_prix_ttc(10.0) == 12.0  # pas 12.000000001

    def test_prix_negatif_leve_exception(self):
        with pytest.raises(ValueError, match='invalide'):
            calcul_prix_ttc(-5.0)

    @pytest.mark.parametrize('ht,ttc', [
        (50.0, 60.0),
        (199.99, 239.99),
        (0.01, 0.01),
    ])
    def test_parametrise(self, ht, ttc):
        assert calcul_prix_ttc(ht) == ttc

# ── TESTS appliquer_coupon ─────────────────────────────────────


class TestAppliquerCoupon:
    def test_reduction_20_pourcent(self, coupon_sample):
        result = appliquer_coupon(100.0, coupon_sample)
        assert result == 80.0

    def test_coupon_inactif_leve_exception(self, db_session):
        coupon_inactif = Coupon(code='OLD', reduction=10.0, actif=False)
        with pytest.raises(ValueError, match='inactif'):
            appliquer_coupon(100.0, coupon_inactif)

    def test_reduction_invalide(self, coupon_sample):
        coupon_invalide = Coupon(code='BAD', reduction=150.0, actif=True)
        with pytest.raises(ValueError):
            appliquer_coupon(100.0, coupon_invalide)

# Ajoutez à la suite de test_pricing.py

    @pytest.mark.parametrize('reduction,prix_initial,prix_attendu', [
        (10, 100.0, 90.0),  # -10%
        (50, 200.0, 100.0),  # -50%
        (100, 50.0, 0.0),  # -100% = gratuit
        (1, 100.0, 99.0),  # -1% minimal
    ])
    def test_coupon_reductions_diverses(self, reduction, prix_initial, prix_attendu, db_session):
        coupon = Coupon(code=f"TEST{reduction}",
                        reduction=float(reduction), actif=True)
        assert appliquer_coupon(prix_initial, coupon) == prix_attendu

    def test_calculer_total_avec_coupon(self):
        p1 = Product(name="P1", price=50.0, stock=10)
        p2 = Product(name="P2", price=30.0, stock=10)
        coupon = Coupon(code="PROMO20", reduction=20.0, actif=True)

        produits = [(p1, 1), (p2, 1)]
        total = calculer_total(produits, coupon)

        assert total == 76.8


class TestCalculerTotalEtRemise:
    def test_calculer_total_panier_vide(self):
        assert calculer_total([]) == 0.0

    def test_calculer_total_sans_coupon(self):
        p1 = Product(name="A", price=10.0, stock=5)
        p2 = Product(name="B", price=20.0, stock=5)
        total = calculer_total([(p1, 2), (p2, 1)])
        # HT = 40, TTC = 48
        assert total == 48.0

    def test_calculer_remise_nominale(self):
        assert calculer_remise(100.0, 80.0) == 20.0

    def test_calculer_remise_prix_original_invalide(self):
        with pytest.raises(ValueError, match="invalide"):
            calculer_remise(0, 10)
