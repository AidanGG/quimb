import pytest
from numpy.testing import assert_allclose

from quimb import (
    prod,
    rand_ket,
    partial_transpose,
)

from quimb.linalg.approx_linalg import (
    get_cntrct_inds_ptr_dot,
    lazy_ptr_dot,
    get_cntrct_inds_ptr_ppt_dot,
    lazy_ptr_ppt_dot,
)

SZS = (5, 4, 3)
DIMS = [2**sz for sz in SZS]


@pytest.fixture
def tri_psi():
    return rand_ket(prod(DIMS))


@pytest.fixture
def bi_psi():
    return rand_ket(prod(DIMS[:-1]))


DIMS_MB = [2] * 11


@pytest.fixture
def psi_mb_abc():
    return rand_ket(prod(DIMS_MB))


@pytest.fixture
def psi_mb_ab():
    return rand_ket(prod(DIMS_MB[:7]))


class TestLazyTensorEval:

    def test_get_cntrct_inds_ptr_dot_simple(self):
        dims = (5, 7)
        sysa = (1,)

        ndim_ab = len(dims)
        dims_a = [d for i, d in enumerate(dims) if i in sysa]

        ci_a_k, ci_ab_b, ci_ab_k = get_cntrct_inds_ptr_dot(
            ndim_ab, sysa)
        assert dims_a == [7]
        assert ci_a_k == [1]
        assert ci_ab_b == [0, 1]
        assert ci_ab_k == [0, 2]

    def test_get_cntrct_inds_ptr_dot_many_body(self):
        dims = (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
        sysa = (1, 2, 3, 4, 8, 9)

        ndim_ab = len(dims)
        dims_a = [d for i, d in enumerate(dims) if i in sysa]

        ci_a_k, ci_ab_b, ci_ab_k = get_cntrct_inds_ptr_dot(
            ndim_ab, sysa)
        assert dims_a == [11, 12, 13, 14, 18, 19]
        assert ci_a_k == [1, 2, 3, 4, 8, 9]
        assert ci_ab_b == list(range(11))
        assert ci_ab_k == [0, 11, 12, 13, 14, 5, 6, 7, 15, 16, 10]

    def test_lazy_ptr_dot_simple(self, tri_psi, bi_psi):
        rho_ab = tri_psi.ptr(DIMS, [0, 1])
        psi_out_expected = rho_ab @ bi_psi
        psi_out_got = lazy_ptr_dot(tri_psi, bi_psi, DIMS, sysa=[0, 1])
        assert_allclose(psi_out_expected, psi_out_got)

    def test_lazy_ptr_dot_manybody(self, psi_mb_abc, psi_mb_ab):
        sysa = [0, 1, 2, 3, 7, 8, 9]
        rho_ab = psi_mb_abc.ptr(DIMS_MB, sysa)
        psi_out_expected = rho_ab @ psi_mb_ab
        psi_out_got = lazy_ptr_dot(psi_mb_abc, psi_mb_ab, DIMS_MB, sysa=sysa)
        assert_allclose(psi_out_expected, psi_out_got)

    def test_get_cntrct_inds_ptr_ppt_dot_simple(self):
        dims = (4, 9, 7)
        sysa = (0,)
        sysb = (1,)

        ndim_abc = len(dims)
        dims_ab = [d for i, d in enumerate(dims)
                   if (i in sysa) or (i in sysb)]

        inds_ab_ket, inds_abc_bra, inds_abc_ket, inds_out = \
            get_cntrct_inds_ptr_ppt_dot(ndim_abc, sysa, sysb)

        assert dims_ab == [4, 9]
        assert inds_ab_ket == [0, 4]
        assert inds_abc_bra == [3, 4, 2]
        assert inds_abc_ket == [0, 1, 2]
        assert inds_out == [3, 1]

    def test_get_cntrct_inds_ptr_ppt_dot_many_body(self):
        dims = (10, 20, 30, 40, 50, 60, 70, 80, 90)
        sysa = (0, 1, 5)
        sysb = (2, 3, 6)

        ndim_abc = len(dims)
        dims_ab = [d for i, d in enumerate(dims)
                   if (i in sysa) or (i in sysb)]

        inds_ab_ket, inds_abc_bra, inds_abc_ket, inds_out = \
            get_cntrct_inds_ptr_ppt_dot(ndim_abc, sysa, sysb)

        assert dims_ab == [10, 20, 30, 40, 60, 70]
        assert inds_ab_ket == [0, 1, 11, 12, 5, 14]
        assert inds_abc_bra == [9, 10, 11, 12, 4, 13, 14, 7, 8]
        assert inds_abc_ket == [0, 1, 2, 3, 4, 5, 6, 7, 8]
        assert inds_out == [9, 10, 2, 3, 13, 6]

    def test_lazy_ptr_ppt_dot(self, tri_psi, bi_psi):
        rho_ab = tri_psi.ptr(DIMS, [0, 1])
        rho_ab_pt = partial_transpose(rho_ab, DIMS[:-1])
        psi_out_expected = rho_ab_pt @ bi_psi
        psi_out_got = lazy_ptr_ppt_dot(tri_psi, bi_psi, DIMS, 0, 1)
        assert_allclose(psi_out_expected, psi_out_got)

    def test_lazy_ptr_ppt_dot_manybody(self, psi_mb_abc, psi_mb_ab):
        sysa = [0, 1, 7, 8]
        sysb = [2, 3, 9]
        rho_ab = psi_mb_abc.ptr(DIMS_MB, sysa + sysb)
        rho_ab = partial_transpose(rho_ab, [2] * 7, sysa=(0, 1, 4, 5))
        psi_out_expected = rho_ab @ psi_mb_ab
        psi_out_got = lazy_ptr_ppt_dot(
            psi_mb_abc, psi_mb_ab, DIMS_MB, sysa=sysa, sysb=sysb)
        assert_allclose(psi_out_expected, psi_out_got)
